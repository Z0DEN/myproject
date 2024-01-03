function logout(){
  localStorage.removeItem('access_key');
  localStorage.removeItem('refresh_key');
  window.location.href = "/logout/";
}
