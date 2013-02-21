// Wrapper for RequireJS. It will make the standard requirejs(), require(), and
// define() functions from Require JS available inside the anonymous function.
//
// See https://edx-wiki.atlassian.net/wiki/display/LMS/Integration+of+Require+JS+into+the+system
(function (requirejs, require, define) {

define(['logme'], function (logme) {
    var BuildView = function (obj, offset, third){
            var View = {
            'draggable': {},
            'icon': {},
            'label' : {},
            'containerEl' : {}
    };

    var draggableObj = obj;
    var target = obj;
    var _this = obj;
    var this_state = obj;
    try{
    View.draggable.html = $(
                    '<div ' +
                        'style=" ' +
                            'position: absolute; ' +
                            'color: black; ' +
                            'font-size: 0.95em; ' +
                        '" ' +
                    '>' +
                        draggableObj.originalConfigObj.label +
                    '</div>');

    View.draggable.css  = {
                    'position': 'absolute',
                    'width': draggableObj.iconWidthSmall,
                    'height': draggableObj.iconHeightSmall,
                    'left': 50 - draggableObj.iconWidthSmall * 0.5,
                    'top': ((draggableObj.originalConfigObj.label.length > 0) ? 5 : 50 - draggableObj.iconHeightSmall * 0.5)
                };

    View.draggable.css2 = {
                    'left': 50 - draggableObj.iconWidthSmall * 0.5,
                    'top': 50 - draggableObj.iconHeightSmall * 0.5
                };


     View.label.html = $(
                        '<div ' +
                            'style=" ' +
                                'position: absolute; ' +
                                'color: black; ' +
                                'font-size: 0.95em; ' +
                            '" ' +
                        '>' +
                            draggableObj.originalConfigObj.label +
                        '</div>');

     View.label.css = {
                        'left': 50 - draggableObj.labelWidth * 0.5,
                        'top': 5 + draggableObj.iconHeightSmall + 5
                    };

    }catch(err){}

    try{
    View.icon.css = {
            'background-color': _this.iconElBGColor,
            'padding-left': _this.iconElPadding,
            'padding-right': _this.iconElPadding,
            'border': _this.iconElBorder,
            'width': _this.iconWidth,
            'height': _this.iconHeight
        };


    View.icon.css2 = {
            'border': 'none',
            'background-color': 'transparent',
            'padding-left': 0,
            'padding-right': 0,
            'z-index': _this.zIndex,
            'width': _this.iconWidthSmall,
            'height': _this.iconHeightSmall,
            'left': 50 - _this.iconWidthSmall * 0.5,
            'top': ((_this.labelEl !== null) ? 5 : 50 - _this.iconHeightSmall * 0.5)
        };

    View.icon.css3 = {
                'border': 'none',
                'background-color': 'transparent',
                'padding-left': 0,
                'padding-right': 0,
                'z-index': _this.zIndex,
                'left': 50 - _this.labelWidth * 0.5,
                'top': 5 + _this.iconHeightSmall + 5
            };
    }catch(err){}

    try{

    if (offset !== undefined) {
        View.icon.css_movetype = {
                'left': target.x - third.iconWidth * 0.5 + offset - third.iconElLeftOffset,
                'top': target.y - third.iconHeight * 0.5 + offset
            };

        View.icon.css_movetype_target = {
                'left': target.offset.left + 0.5 * target.w - third.iconWidth * 0.5 + offset - third.iconElLeftOffset,
                'top': target.offset.top + 0.5 * target.h - third.iconHeight * 0.5 + offset
            };

        View.label.css3 = {
                    'left': target.x - third.labelWidth * 0.5 + offset - 9, // Account for padding, border.
                    'top': target.y - third.iconHeight * 0.5 + third.iconHeight + 5 + offset
                };

        View.label.css3_target = {
                    'left': target.offset.left + 0.5 * target.w - third.labelWidth * 0.5 + offset - 9, // Account for padding, border.
                    'top': target.offset.top + 0.5 * target.h + third.iconHeight * 0.5 + 5 + offset
                };
        }

    }catch(err){}


    try{
    View.label.html_obj = $(
                        '<div ' +
                            'style=" ' +
                                'position: absolute; ' +
                                'color: black; ' +
                                'font-size: 0.95em; ' +
                            '" ' +
                        '>' +
                            obj.label +
                        '</div>');
    }catch(err){}


    try{
    View.label.css2 = {
                'background-color': this_state.config.labelBgColor,
                'padding-left': 8,
                'padding-right': 8,
                'border': '1px solid black'
            };
    }catch(err){}

    View.containerEl.html =  $(
            '<div ' +
                'style=" ' +
                    'width: 100px; ' +
                    'height: 100px; ' +
                    'display: inline; ' +
                    'float: left; ' +
                    'overflow: hidden; ' +
                    'border-left: 1px solid #CCC; ' +
                    'border-right: 1px solid #CCC; ' +
                    'text-align: center; ' +
                    'position: relative; ' +
                '" ' +
                '></div>');

        return View;
    };

    return BuildView;

});
// End of wrapper for RequireJS. As you can see, we are passing
// namespaced Require JS variables to an anonymous function. Within
// it, you can use the standard requirejs(), require(), and define()
// functions as if they were in the global namespace.
}(RequireJS.requirejs, RequireJS.require, RequireJS.define)); // End-of: (function (requirejs, require, define)
