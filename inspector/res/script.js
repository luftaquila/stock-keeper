$(function() {
  (function () { var script = document.createElement('script'); script.src="//cdn.jsdelivr.net/npm/eruda"; document.body.appendChild(script); script.onload = function () { eruda.init() } })();
  $.ajax({
    url: '/stock/data/db.json',
    beforeSend : function() { gauge(0); },
    xhr: function() { // XMLHttpRequest redefinition
      let xhr = $.ajaxSettings.xhr();
      xhr.onprogress = function(e) { gauge(Math.floor(e.loaded / e.total * 100)); };
      return xhr;
    },
    success : function(data) {
      console.log( data );
    }
  });
});

function gauge(per) {
  if(!per) $('#percent').css('display', 'flex');
  $('#gauge').removeClass(function (i, c) { return (c.match (/(^|\s)p\S+/g) || []).join(' '); }).addClass('p' + per);
  $('#gauge span').text(per + '%');
  if(per == 100) setTimeout(function() { $('#percent').css('display', 'none'); }, 1000);
}