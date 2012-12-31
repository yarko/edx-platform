class @VideoCaption extends Subview
  initialize: ->
    # Properties which will control the automatic hiding/showing of captions.
    # We need to remember how captions were opened - by a mouse click on the
    # CC icon, or by a mouse enter event. Then we can determine whether to
    # allow automatic hiding of captions by mouse leave event or not.
    @disableMouseLeave = false
    @captionsOpenWithClick = false
    @captionsOpenWithMouse = false

    @loaded = false

  bind: ->
    $(window).bind('resize', @resize)
    @$('.hide-subtitles').click @toggle
    @$('.subtitles').mouseenter(@onMouseEnter).mouseleave(@onMouseLeave)
      .mousemove(@onMovement).bind('mousewheel', @onMovement)
      .bind('DOMMouseScroll', @onMovement)

  captionURL: ->
    "/static/#{@captionDataDir}/subs/#{@youtubeId}.srt.sjson"

  render: ->
    # TODO: make it so you can have a video with no captions.
    #@$('.video-wrapper').after """
    #  <ol class="subtitles"><li>Attempting to load captions...</li></ol>
    #  """
    @$('.video-wrapper').after """
      <ol class="subtitles"></ol>
      """
    @$('.video-controls .secondary-controls').append """
      <a href="#" class="hide-subtitles" title="Turn off captions">Captions</a>
      """#"
    @$('.subtitles').css maxHeight: @$('.video-wrapper').height() - 5
    @fetchCaption()

  fetchCaption: ->
    $.getWithPrefix @captionURL(), (captions) =>
      @captions = captions.text
      @start = captions.start

      @loaded = true

      if onTouchBasedDevice()
        $('.subtitles li').html "Caption will be displayed when you start playing the video."
      else
        @renderCaption()

  renderCaption: ->
    container = $('<ol>')

    $.each @captions, (index, text) =>
      container.append $('<li>').html(text).attr
        'data-index': index
        'data-start': @start[index]

    @$('.subtitles').html(container.html())
    @$('.subtitles li[data-index]').click @seekPlayer

    # prepend and append an empty <li> for cosmetic reason
    @$('.subtitles').prepend($('<li class="spacing">').height(@topSpacingHeight()))
      .append($('<li class="spacing">').height(@bottomSpacingHeight()))

    @rendered = true

  search: (time) ->
    if @loaded
      min = 0
      max = @start.length - 1

      while min < max
        index = Math.ceil((max + min) / 2)
        if time < @start[index]
          max = index - 1
        if time >= @start[index]
          min = index
      return min

  play: ->
    if @loaded
      @renderCaption() unless @rendered
      @playing = true

  pause: ->
    if @loaded
      @playing = false

  updatePlayTime: (time) ->
    if @loaded
      # This 250ms offset is required to match the video speed
      time = Math.round(Time.convert(time, @currentSpeed, '1.0') * 1000 + 250)
      newIndex = @search time

      if newIndex != undefined && @currentIndex != newIndex
        if @currentIndex
          @$(".subtitles li.current").removeClass('current')
        @$(".subtitles li[data-index='#{newIndex}']").addClass('current')

        @currentIndex = newIndex
        @scrollCaption()

  resize: =>
    @$('.subtitles').css maxHeight: @captionHeight()
    @$('.subtitles .spacing:first').height(@topSpacingHeight())
    @$('.subtitles .spacing:last').height(@bottomSpacingHeight())
    @scrollCaption()

  onMouseEnter: =>
    clearTimeout @frozen if @frozen
    @frozen = setTimeout @onMouseLeave, 10000

  onMovement: =>
    @onMouseEnter()

  onMouseLeave: =>
    clearTimeout @frozen if @frozen
    @frozen = null
    @scrollCaption() if @playing

  scrollCaption: ->
    if !@frozen && @$('.subtitles .current:first').length
      @$('.subtitles').scrollTo @$('.subtitles .current:first'),
        offset: - @calculateOffset(@$('.subtitles .current:first'))

  seekPlayer: (event) =>
    event.preventDefault()
    time = Math.round(Time.convert($(event.target).data('start'), '1.0', @currentSpeed) / 1000)
    $(@).trigger('seek', time)

  calculateOffset: (element) ->
    @captionHeight() / 2 - element.height() / 2

  topSpacingHeight: ->
    @calculateOffset(@$('.subtitles li:not(.spacing):first'))

  bottomSpacingHeight: ->
    @calculateOffset(@$('.subtitles li:not(.spacing):last'))

  toggle: (event) =>
    event.preventDefault()
    if @el.hasClass('closed') # Captions are "closed" e.g. turned off
      # We can reach this point only when the user clicks the CC button. This
      # means that we must disable mouse enter/mouse leave caption show/hide
      # until the user clicks the CC button again (to hide captions).
      @captionsOpenWithClick = true
      @disableMouseLeave = true

      @hideCaptions(false)
    else # Captions are on
      if @captionsOpenWithClick is false
        # If we were called, and reached this point, then this means that
        # initially the captions were requested to be open (setting set in
        # cookies). We must simulate a user click on the CC button, so that the
        # rest of the mouse enter/mouse leave caption show/hide code works next
        # time.
        @captionsOpenWithClick = true
        @captionsOpenWithMouse = false
        @disableMouseLeave = true
        @el.parent().find('.hide-subtitles').addClass("selected")
        return

      # A request to hide captions was made. Enable showing of captions with a
      # mouse enter event.
      @captionsOpenWithClick = false
      @disableMouseLeave = false

      @hideCaptions(true)

  hideCaptions: (hide_captions) =>
    if hide_captions
      @el.find('.hide-subtitles').removeClass("selected")
      @$('.hide-subtitles').attr('title', 'Turn on captions')
      @el.addClass('closed')

      # When the captions are being hidden, we will show the right vertical bar
      # with the arrow, and the area which triggers the showing of captions on
      # mouse enter event.
      @el.find('.video_caption_vert_bar').each (index, value) ->
        $(value).show()

        # A smooth animation for the arrow - slide it, and hide it partially
        # from the user's view.
        $(value).find('.cvb_image').each (index, value) ->
          # The first time the animation takes a bit longer, so we will skip if
          # the first time has not completed yet.
          if $(value).attr('first_time_show') is undefined
            return

          $(value).css('margin-left', '0px')
          $(value).animate
            'margin-left': '8'
          , 1000

      @el.find('.cvb_mouseenter_area').show()

    else
      # Hide the right vertical bar with arrow, and disable the area that
      # triggers the showing of captions on mouse enter.
      @el.find('.video_caption_vert_bar').hide();
      @el.find('.cvb_mouseenter_area').hide();

      # If we were called from a click on the CC button, lets disable the mouse
      # enter/mouse leave caption show/hide functionality.
      if @captionsOpenWithMouse is false
          @disableMouseLeave = true
          @captionsOpenWithClick = true
          @el.parent().find('.hide-subtitles').addClass("selected")

      @$('.hide-subtitles').attr('title', 'Turn off captions')
      @el.removeClass('closed')
      @scrollCaption()
    $.cookie('hide_captions', hide_captions, expires: 3650, path: '/')

  captionHeight: ->
    if @el.hasClass('fullscreen')
      $(window).height() - @$('.video-controls').height()
    else
      @$('.video-wrapper').height()
