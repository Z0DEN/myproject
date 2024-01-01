async function fetchTokens() {
  try {
    const response = await fetch('https://192.168.0.98/GetToken/');
    if (!response.ok) {
      throw new Error('Ошибка при получении токенов');
    }
    const json = await response.json();
    
    localStorage.setItem('access_token', json.access_token);
    localStorage.setItem('refresh_token', json.refresh_token);

    console.log('Токены сохранены в localStorage:', json.msg);
  } catch (error) {
    console.error(error);
  }
}

if (localStorage.getItem('access_token') == null){
  console.log('gettin new tokens')
	fetchTokens();
}
