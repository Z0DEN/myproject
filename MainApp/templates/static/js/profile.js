const access_token = Cookies.get('access_token')
let response_data;

function get_data_main(func='test') {
 fetch(`https://${node_domain}.whoole.space:8002/${func}/`, {
   method: 'POST',
   headers: {
     'Content-Type': 'application/json',
     'Authorization': `user Bearer ${access_token}`
   },
   body: JSON.stringify({
     username: username,
   })
 })
 .then(response => response.json())
 .then(data => {
   console.log(data);
   response_data = data;
   checkStatus();
 })
 .catch((error) => {
   console.error('Error:', error);
 });
}

function checkStatus() {
 if (response_data.status == 14 || response_data.status == 15){
   console.log('logout')
 } else if (response_data.status == 31){
   get_data_main();
 }
}

get_data_main();

function logout(){
  window.location.href = "/logout/";
}
