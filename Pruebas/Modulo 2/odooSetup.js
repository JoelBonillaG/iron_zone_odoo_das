import { ADMIN_USER, LOCAL_BASE_URL, buildUrl } from "./testHelpers.js";

const DB = process.env.IRONZONE_DB || "iron_zone";

function mergeCookies(currentCookie, setCookieHeader) {
    if (!setCookieHeader) {
        return currentCookie;
    }
    const nextCookie = setCookieHeader
        .split(",")
        .map((cookie) => cookie.split(";")[0].trim())
        .filter(Boolean)
        .join("; ");
    return [currentCookie, nextCookie].filter(Boolean).join("; ");
}

async function jsonRpc(url, payload, cookie = "") {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...(cookie ? { Cookie: cookie } : {}),
        },
        body: JSON.stringify({
            jsonrpc: "2.0",
            method: "call",
            params: payload,
        }),
    });
    const body = await response.json();
    if (body.error) {
        const message = body.error.data?.message || body.error.message || JSON.stringify(body.error);
        throw new Error(message);
    }
    return {
        result: body.result,
        cookie: mergeCookies(cookie, response.headers.get("set-cookie")),
    };
}

export async function createAdminSession(baseUrl = LOCAL_BASE_URL) {
    const candidates = [
        { login: ADMIN_USER.email, password: ADMIN_USER.password },
        { login: "admin@ironzone.com", password: "admin123" },
        { login: "admin", password: "admin123" },
    ];
    let lastError;
    for (const candidate of candidates) {
        try {
            const auth = await jsonRpc(buildUrl(baseUrl, "/web/session/authenticate"), {
                db: DB,
                login: candidate.login,
                password: candidate.password,
            });
            if (auth.result?.uid) {
                return {
                    baseUrl,
                    cookie: auth.cookie,
                };
            }
        } catch (error) {
            lastError = error;
        }
    }
    throw new Error(`No se pudo autenticar como administrador para preparar datos. ${lastError?.message || ""}`);
}

export async function adminCall(session, model, method, args = [], kwargs = {}) {
    const url = buildUrl(session.baseUrl, `/web/dataset/call_kw/${model}/${method}`);
    const response = await jsonRpc(url, {
        model,
        method,
        args,
        kwargs,
    }, session.cookie);
    session.cookie = response.cookie;
    return response.result;
}

export async function xmlId(session, value) {
    const [module, name] = value.split(".");
    const rows = await adminCall(session, "ir.model.data", "search_read", [[
        ["module", "=", module],
        ["name", "=", name],
    ]], {
        fields: ["res_id"],
        limit: 1,
    });
    if (!rows.length) {
        throw new Error(`No se encontro XML-ID ${value}`);
    }
    return rows[0].res_id;
}

export async function ensureDemoPaymentEnabled(session) {
    const providerIds = await adminCall(session, "payment.provider", "search", [[["code", "=", "demo"]]], { limit: 1 });
    if (providerIds.length) {
        await adminCall(session, "payment.provider", "write", [providerIds, {
            state: "test",
            is_published: true,
            allow_tokenization: false,
            allow_express_checkout: false,
        }]);
    }

    const methodIds = await adminCall(session, "payment.method", "search", [[["code", "=", "demo"]]], { limit: 1 });
    if (methodIds.length) {
        await adminCall(session, "payment.method", "write", [methodIds, { active: true }]);
    }
}

export async function ensurePortalUser(session, user) {
    const existingIds = await adminCall(session, "res.users", "search", [[["login", "=", user.email]]], { limit: 1 });
    if (existingIds.length) {
        await adminCall(session, "res.users", "write", [existingIds, {
            active: true,
            password: user.password,
        }]);
        return existingIds[0];
    }

    const portalGroupId = await xmlId(session, "base.group_portal");
    const userId = await adminCall(session, "res.users", "create", [[{
        name: user.name,
        login: user.email,
        email: user.email,
        password: user.password,
        groups_id: [[6, 0, [portalGroupId]]],
    }]]);
    const normalizedUserId = Array.isArray(userId) ? userId[0] : userId;
    const [createdUser] = await adminCall(session, "res.users", "read", [[normalizedUserId]], {
        fields: ["partner_id"],
    });
    const partnerId = createdUser?.partner_id?.[0];
    if (partnerId) {
        const partnerFields = await adminCall(session, "res.partner", "fields_get", [], {
            attributes: ["type"],
        });
        const countryIds = await adminCall(session, "res.country", "search", [[["code", "=", "EC"]]], { limit: 1 });
        const values = {
            phone: user.phone,
            mobile: user.phone,
            email: user.email,
            street: "Av. Amazonas N34-120",
            city: "Quito",
            vat: user.vat || "1804888764",
        };
        if (countryIds.length) {
            values.country_id = countryIds[0];
        }
        if (partnerFields.l10n_latam_identification_type_id) {
            const typeIds = await adminCall(session, "l10n_latam.identification.type", "search", [[
                "|",
                ["name", "ilike", "Cedula"],
                ["name", "ilike", "Cédula"],
            ]], { limit: 1 });
            if (typeIds.length) {
                values.l10n_latam_identification_type_id = typeIds[0];
            }
        }
        if (partnerFields.iz_gender) {
            values.iz_gender = user.gender || "male";
        }
        await adminCall(session, "res.partner", "write", [[partnerId], values]);
    }
    return normalizedUserId;
}

export async function ensureUserGroups(session, login, xmlIds) {
    const userIds = await adminCall(session, "res.users", "search", [[["login", "=", login]]], { limit: 1 });
    if (!userIds.length) {
        throw new Error(`No se encontro el usuario ${login}`);
    }
    const groupIds = [];
    for (const xmlIdValue of xmlIds) {
        groupIds.push(await xmlId(session, xmlIdValue));
    }
    await adminCall(session, "res.users", "write", [userIds, {
        groups_id: groupIds.map((groupId) => [4, groupId]),
    }]);
    return userIds[0];
}

export async function activateLatestSubscriptionForUser(session, userEmail) {
    const userRows = await adminCall(session, "res.users", "search_read", [[["login", "=", userEmail]]], {
        fields: ["partner_id"],
        limit: 1,
    });
    const partnerId = userRows[0]?.partner_id?.[0];
    if (!partnerId) {
        throw new Error(`No se encontro partner para ${userEmail}`);
    }
    const subscriptions = await adminCall(session, "sale.subscription", "search_read", [[["partner_id", "=", partnerId]]], {
        fields: ["id", "stage_type"],
        order: "id desc",
        limit: 1,
    });
    if (!subscriptions.length) {
        throw new Error(`No se encontro suscripcion creada para ${userEmail}`);
    }
    if (subscriptions[0].stage_type !== "in_progress") {
        await adminCall(session, "sale.subscription", "action_start_subscription", [[subscriptions[0].id]]);
    }
    return subscriptions[0].id;
}

export async function latestInvoiceForUser(session, userEmail) {
    const userRows = await adminCall(session, "res.users", "search_read", [[["login", "=", userEmail]]], {
        fields: ["partner_id"],
        limit: 1,
    });
    const partnerId = userRows[0]?.partner_id?.[0];
    const invoices = await adminCall(session, "account.move", "search_read", [[
        ["partner_id", "=", partnerId],
        ["move_type", "=", "out_invoice"],
    ]], {
        fields: ["id", "name", "payment_state", "amount_total"],
        order: "id desc",
        limit: 1,
    });
    return invoices[0] || null;
}

export async function ensureLatestOrderInvoice(session, userEmail) {
    const userRows = await adminCall(session, "res.users", "search_read", [[["login", "=", userEmail]]], {
        fields: ["partner_id"],
        limit: 1,
    });
    const partnerId = userRows[0]?.partner_id?.[0];
    if (!partnerId) {
        throw new Error(`No se encontro partner para ${userEmail}`);
    }

    let invoice = await latestInvoiceForUser(session, userEmail);
    if (invoice) {
        return invoice;
    }

    const orders = await adminCall(session, "sale.order", "search_read", [[
        ["partner_id", "=", partnerId],
        ["state", "in", ["sale", "done"]],
    ]], {
        fields: ["id", "name", "invoice_ids"],
        order: "id desc",
        limit: 1,
    });
    if (!orders.length) {
        return null;
    }

    if (!orders[0].invoice_ids?.length) {
        await adminCall(session, "sale.order", "_create_invoices", [[orders[0].id]]);
    }

    const invoices = await adminCall(session, "account.move", "search_read", [[
        ["invoice_origin", "=", orders[0].name],
        ["move_type", "=", "out_invoice"],
    ]], {
        fields: ["id", "name", "payment_state", "amount_total", "state"],
        order: "id desc",
        limit: 1,
    });
    if (invoices.length && invoices[0].state === "draft") {
        await adminCall(session, "account.move", "action_post", [[invoices[0].id]]);
    }
    invoice = await latestInvoiceForUser(session, userEmail);
    return invoice;
}

export async function ensurePreviousEventRegistration(session, userEmail) {
    const userRows = await adminCall(session, "res.users", "search_read", [[["login", "=", userEmail]]], {
        fields: ["partner_id", "name", "email"],
        limit: 1,
    });
    const user = userRows[0];
    const partnerId = user?.partner_id?.[0];
    if (!partnerId) {
        throw new Error(`No se encontro partner para ${userEmail}`);
    }

    const existingCount = await adminCall(session, "event.registration", "search_count", [[
        ["partner_id", "=", partnerId],
        ["state", "!=", "cancel"],
    ]]);
    if (existingCount > 0) {
        return;
    }

    const events = await adminCall(session, "event.event", "search_read", [[
        ["website_published", "=", true],
    ]], {
        fields: ["id", "name"],
        order: "date_begin asc",
        limit: 1,
    });
    if (!events.length) {
        throw new Error("No se encontro evento para preparar historial previo.");
    }

    await adminCall(session, "event.registration", "create", [[{
        event_id: events[0].id,
        partner_id: partnerId,
        name: user.name || userEmail,
        email: user.email || userEmail,
    }]]);
}
