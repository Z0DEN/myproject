var delay = 500;
var timer = null
const img_checkbox = document.getElementById('checkbox').style;
const img_cross = document.getElementById('cross').style;

$('#id_username').on('input', function() {
 var username = $(this).val();

 img_checkbox.animation = '1'
 img_cross.animation = '1'
 clearTimeout(timer);
 if (username.trim() === ""){
   img_cross.animation = 'appearance 3000ms ease-in-out forwards';
   return;
 }
 timer = setTimeout(function() {
   $.ajax({
     url: '/CheckUsername/',
     data: {
       'username': username
     },
     success: function(data) {
       if (data.is_taken) {
    	  img_cross.animation = 'appearance 3000ms ease-in-out forwards';
       }
       else {
    	  img_checkbox.animation = 'appearance 3000ms ease-in-out forwards';
       }
     }
   });
 }, delay);
});
