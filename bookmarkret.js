javascript:(function(){
    if (!location.href.match(/^https:\/\/chunithm-net.com/)) {
        alert("CHUNITHM NETを開いた状態でしてください");
        throw Error();
    }
    window.name = 'CHUNITHM ■ CHUNITHM-NET';
    var html = '<form method="post" action="http://localhost:7777/chunithm.api" id="postjump" target=_brunk style="display: none;"><input type="hidden" name="userid" value="' + document.cookie + '" ></form>';
    $("body").append(html);
    $('#postjump').submit();
    $('#postjump').remove();
})(document);