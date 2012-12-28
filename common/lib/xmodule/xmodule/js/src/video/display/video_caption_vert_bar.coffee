class @VideoCaptionVertBar extends Subview
  initialize: ->

  bind: ->

  render: ->
    _this = this

    @vertBarEl = $('<div class="video_caption_vert_bar"></div>');

    @vertBarMouseEnterEl = $('<div class="cvb_mouseenter_area"></div>');
    @vertBarMouseEnterEl.appendTo(@el);

    @vertBarMouseEnterEl.mouseenter (event) ->
      unless event.offsetX
        event.offsetX = (event.pageX - $(event.target).offset().left)
        event.offsetY = (event.pageY - $(event.target).offset().top)

      if _this.videoPlayer.caption.el.hasClass("closed") is true
        _this.videoPlayer.caption.captionsOpenWithMouse = true
        _this.videoPlayer.caption.hideCaptions false

    @vertBarImageEl = $('<div class="cvb_image"></div>');
    @vertBarImageEl.appendTo(@vertBarEl);

    @el.append(@vertBarEl);

    _this = this
    setInterval (->
      _this.vertBarImageEl.animate
        "margin-left": "8"
      , 1000, ->
        _this.vertBarImageEl.attr 'first_time_show', 'done'
    ), 5000
