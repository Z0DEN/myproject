async function fetchTokens() {
  try {
    const response = await fetch('https://192.168.0.98/GetToken/');
    if (!response.ok) {
      throw new Error('error while getting tokens');
    }
    const json = await response.json();
    
    localStorage.setItem('access_token', json.access_token);
    localStorage.setItem('refresh_token', json.refresh_token);

  } catch (error) {
    console.error(error);
  }
}

if (localStorage.getItem('access_token') == null){
	fetchTokens();
}

function logout(){
  localStorage.removeItem('access_key');
  localStorage.removeItem('refresh_key');
  window.location.href = "/logout/";
}
