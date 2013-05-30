(function () {
<<<<<<< Updated upstream
    var timeout = 120;

    // This function should only run once, even if there are multiple jsinputs
    // on a page.
    if (typeof(_editamolecule_loaded) == 'undefined' || _editamolecule_loaded === false) {
        _editamolecule_loaded = true;
        loadGWTScripts();
        waitForGWT();
    } else {
        return;
    }

    var allElems = [] ;
=======

>>>>>>> Stashed changes

    // Define an class (functional pattern) that will be instantiated for each
    // jsinput element of the DOM
    var jsinputConstructor = function (spec, clsm) {
        // 'that' is the object returned by the constructor. It holds public
        // methods
        var that;


        // private methods
        var getParent = function (elem) { return $(elem).parent() ; };
        var inputfield =  function (parent, id) {
            return parent.find('input[id=jsinput' + id);
        };

        // public methods
        that.id = function () { return spec.id ; };
        that.elem = function () { return spec.elem ; };
        that.parent = function () { return getParent(spec.elem);};
<<<<<<< Updated upstream
        that.problem = function () { 
=======
        that.problem = function () {
>>>>>>> Stashed changes
            return $(elem).closest("section.problem");
        };

        checkbutton.onMouseOver(checkfn());
        allElems.push(that);
        return that;
    };

    // Find all jsinput elements, and create a jsinput object for each one
    var walkDOM = function () {
        var all = $(document).find('section[class="jsinput"]');
        var newid;
        for (i = 0; i++; i < all.length) {
            // Get just the mako variable 'id' from the id attribute
            newid = all[i].getAttribute("id").replace(/^inputtype_/, "");
            var newJsElem = jsinputConstructor({
                id: newid ,
                elem: all[i]
            });
        }
    };

<<<<<<< Updated upstream
=======
    // This function should only run once, even if there are multiple jsinputs
    // on a page.
    if (typeof(_jsinput_loaded) == 'undefined' || _jsinput_loaded === false) {
        _jsinput_loaded = true;
        walkDOM();

    } else {
        return;
    }

    var allElems = [] ;
>>>>>>> Stashed changes
}).call(this);
