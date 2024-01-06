$('#login-form').on('submit', function(e) {
 e.preventDefault();

 $.ajax({
    type: $(this).attr('method'),
    url: $(this).attr('action'),
    data: $(this).serialize(),
    success: function(response) {
        var accessToken = response.access_token;
        var status = response.status;
        if (status === 24){
          localStorage.setItem('access_token', accessToken);
          window.location.href = '/profile/';
        }
    }
 });
});
