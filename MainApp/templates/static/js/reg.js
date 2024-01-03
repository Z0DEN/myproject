var timeoutId = null;
var minLength = 3;

$('#id_username').on('input', function(){
 var username = $(this).val();

 if (timeoutId !== null) {
   clearTimeout(timeoutId);
 }

 if (username.length >= minLength) {
   timeoutId = setTimeout(function() {
     $.ajax({
       url: '/CheckUsername/',
       data: {
         'username': username
       },
       success: function(data){
         if (data.is_taken){
		 console.log('username is taken')
         }
	 else {
		 console.log('username is free')
	 }
       }
     });
   }, 500);
 }
});

