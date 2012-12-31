# Create a right vertical bar with an arrow, and an area to attach a mouse
# enter event which will trigger the showing of captions.
#
# The hiding of captions will be attached to the captions DIV triggered on a
# mouse leave event.
#
# Please see video_player.coffe and video_caption.coffe for the rest of the
# functionality. Especially the functions:
#     VideoPlayer.bind()
#     VideoPlayer.render()
#
#     VideoCaptions.initialize()
#     VideoCaptions.toggle()
#     VideoCaptions.hideCaption()
class @VideoCaptionVertBar extends Subview
  initialize: ->

  bind: ->

  render: ->
    _this = this

    @vertBarEl = $('<div class="video_caption_vert_bar"></div>');

    # Create the DIV to attach a mouse enter event for showing of captions.
    @vertBarMouseEnterEl = $('<div class="cvb_mouseenter_area"></div>');
    @vertBarMouseEnterEl.appendTo(@el);

    @vertBarMouseEnterEl.mouseenter (event) ->
      if _this.videoPlayer.caption.el.hasClass("closed") is true
        _this.videoPlayer.caption.captionsOpenWithMouse = true
        _this.videoPlayer.caption.hideCaptions false

    # Create the DIV that will contain the right vertical bar with arrow.
    @vertBarImageEl = $('<div class="cvb_image"></div>');
    @vertBarImageEl.appendTo(@vertBarEl);

    @el.append(@vertBarEl);

    # The first time, we will hide the right vertical bar with arrow after a 5
    # second delay. Next time, it will be without a delay - just 1000ms to
    # hide it partially.
    setInterval (->
      _this.vertBarImageEl.animate
        "margin-left": "8"
      , 1000, ->
        _this.vertBarImageEl.attr 'first_time_show', 'done'
    ), 5000
