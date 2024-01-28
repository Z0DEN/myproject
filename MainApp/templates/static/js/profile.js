const csrf_cookie = Cookies.get('csrftoken')
let access_token;
let response_data;


function mainFunc(){
  console.log('start main function')
}


function updateTokens(){
 console.log('start updating tokens');
 fetch('https://whoole.space/UserTokenUpdate/', {
   method: 'POST',
   headers: {
     'Content-Type': 'application/json',
     'X-CSRFToken': csrf_cookie, 
   },
 })
 .then(response => response.json())
 .then(data => {
   console.log(data);
   if data.status != 23{
      window.location.href = "/logout/";
   }
 })
}


function makeRequest(func='test') {
 access_token = Cookies.get('access_token');
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
 status = response_data.status
 if (status == 14 || status == 15){
   updateTokens()
 } else if (status == 31){
   makeRequest();
 } else if (status == 22){
   mainFunc()
 }
}

makeRequest();


function logout(){
  window.location.href = "/logout/";
}
