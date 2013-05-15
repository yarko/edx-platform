(function () {

    initialize
    function initialize(elem) {
    // Find DOM elements that are needed for initialization, then call the
    // script, passing the relevant data.
        var parent = $(elem).parent();
        var input_field = parent.find('input[id*="jsinput"]');
        var value = input_field.val();
        var placeholder = parent.find(".script_placeholder");
        var checkfn = $(placeholder).data('check');
        var src = $(placeholder).data('src');
        loadScript(src);
    }

    function loadScript(src) {
        var script = document.createElement('script');
        script.setAttribute('type', 'text/javascript');
        script.setAttribute('src',  src);
        $('head')[0].appendChild(script);
    }

    function preSubmit(checkfn, input_field) {
        input_field.val(checkfn())
    }
})
