// This scripts connects category completion to sub category completion

function category_completion(category_selector, category_sub_selector){
    $(document).ready(function() {
        // initial value
        var category_select = $(category_selector);
        var category_id = category_select.val();

        if (category_id){
            var sub_category_select = $(category_sub_selector);
            var sub_category_widget = sub_category_select.parents('.autocomplete-light-widget');
            sub_category_widget.yourlabsWidget().autocomplete.data = {
                'parent': category_id[0]};
        }

        category_select.change(function() {
            var sub_category_select = $(category_sub_selector);
            var sub_category_widget = sub_category_select.parents('.autocomplete-light-widget');
            var value = $(this).val();
            if (value) {
                category_id = value[0];
            }

            if (category_id){
                sub_category_widget.yourlabsWidget().autocomplete.data = {
                    'parent': category_id};
            }
            else {
                sub_category_widget.yourlabsWidget().autocomplete.data = {}
            }
        })
    });
}

