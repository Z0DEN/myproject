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
   if (data.status != 23){
      window.location.href = "/logout/";
   }
 })
}


function createFile(){
  let input = document.getElementById("file-input");
  
  let files = input.files;

  if (files.length > 0) {
    console.log(files.length)
  } else {
    console.log("Файлы не выбраны");
  }
}


function getUserData(){
 console.log('start gettin data')
 body = {
   test: 'test'
 }
 makeRequest('GetUserData', body)
  .then(function(resp_data) {
    console.log('response data: ', resp_data)
  })
}


function makeRequest(func='GetUserData', body={}) {
 access_token = Cookies.get('access_token');
 fetch(`https://${node_domain}.whoole.space:8002/${func}/`, {
   method: 'POST',
   headers: {
     'Content-Type': 'application/json',
     'Authorization': `user Bearer ${access_token}`
   },
   body: JSON.stringify({
     username: username,
     ...body,
   })
 })
 .then(response => response.json())
 .then(data => {
   console.log(data);
   status = data.token_validate_status
   if (status == 22){
     return data
   } else if (status == 14 || status == 15){
     upd_tokens_status = updateTokens()
     return makeRequest(func, body)
   } else if (status == 31){
     return makeRequest(func, body)
   }
   })
 .catch((error) => {
   console.error('Error:', error);
 });
}


function logout(){
  window.location.href = "/logout/";
}
