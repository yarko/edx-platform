(function() {
  $(document).ready(function() {
    // Show/Hide chat block
    $('#chat_wrapper .chat_toggle').click(function() {
      $('#chat_block').show();
      if ($(this).hasClass('closed')) {
        $('#chat_block').show();
        $(this).toggleClass('closed').siblings().animate({height: '400px'}, 'slow', function() {
          $(this).siblings().find('span.openChat').hide();
          $(this).siblings().find('span.closeChat').show();
          $('#chatPopout').show();
        });
      } else {
        $(this).toggleClass('closed').siblings().animate({height: '0px'}, 'slow', function() {
          $(this).siblings().find('span.openChat').show();
          $(this).siblings().find('span.closeChat').hide();
        });
        $('#chatPopout').hide();
      }
    });

    var chatWindow, chatFrameRef, newChatFrame;
    $('#chatPopout').click(function() {
      $('#chat_wrapper, #chatPopin').toggle();

      chatFrameRef = $('#chat_block').attr('src');
      newChatFrame = '<iframe id="chat_block" src="' + chatFrameRef + '"></iframe>';
      $('#chat_block').remove();
      chatWindow = window.open(chatFrameRef, "{{ course.title }}", "width=800, height=600");

      $('#chatPopin').click(function() {
        chatWindow.close();
      });

      $(chatWindow).unload(function() {
        if (this.document.location.href.indexOf(chatFrameRef) >= 0) {
          $('#chat_frame_wrapper').html(newChatFrame);
          $('#chat_block').show();
          $('#chat_wrapper, #chatPopin').toggle();
        }
      });
    });
  });
})($);
