class @VideoCaptionVertBar extends Subview
  initialize: ->

  bind: ->

  render: ->
    @vertBarEl = $('<div class="video_caption_vert_bar"></div>');

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
