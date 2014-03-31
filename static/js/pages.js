
$(document).ready(function($) {
    function goPage(hash) {
        
        var data = hash.substr(1).split("/");
        var page = data.shift();
        var target = $('#'+page);
        if (!target)
          return;
        // change the page
        target.siblings().attr('hidden', 'true');
        target.removeAttr('hidden');
    }

    $(window).bind( 'hashchange', function(e) {
        goPage( location.hash ? location.hash : '#messages' );
    });
});

