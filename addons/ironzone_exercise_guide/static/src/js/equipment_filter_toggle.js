odoo.define('ironzone_exercise_guide.equipment_filter_toggle', function (require) {
    'use strict';

    var core = require('web.core');

    $(document).ready(function () {
        function findEquipmentWidget() {
            var $input = $("[name='equipment_id'], select[name='equipment_id'], input[name='equipment_id']");
            if ($input.length) {
                var $container = $input.closest('.o_searchview_input, .o_searchview_field, .o_search_panel, .o_search_options');
                if (!$container.length) {
                    $container = $input.parent();
                }
                return {input: $input, container: $container};
            }
            return null;
        }

        function toggle() {
            var withMachine = $('.o_searchview .o_search_panel a').filter(function () {
                return $(this).text().trim().indexOf('Con maquina') !== -1 || $(this).text().trim().indexOf('Con máquina') !== -1;
            });
            var found = findEquipmentWidget();
            if (!found) {
                return;
            }
            var active = withMachine.hasClass('active');
            if (active) {
                found.container.removeClass('o_hidden');
            } else {
                found.container.addClass('o_hidden');
                found.input.val('');
            }
        }

        toggle();
        $(document).on('click', '.o_searchview .o_search_panel a', function () {
            setTimeout(toggle, 50);
        });
    });
});
