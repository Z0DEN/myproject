const csrf_cookie = Cookies.get('csrftoken')
let access_token;
let response_data;


function mainFunc(){
  console.log('start main function')
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


async function updateTokens(){
 console.log('start updating tokens');
 let response = await fetch('https://whoole.space/UserTokenUpdate/', {
   method: 'POST',
   headers: {
     'Content-Type': 'application/json',
     'X-CSRFToken': csrf_cookie,
   },
 });
 let data = await response.json();
 console.log(data);
 if (data.status != 23){
      window.location.href = "/logout/";
 }
 return data.status;
}


async function makeRequest(func='GetUserData', body={}) {
 try {
   access_token = Cookies.get('access_token');
   let response = await fetch(`https://${node_domain}.whoole.space:8002/${func}/`, {
     method: 'POST',
     headers: {
       'Content-Type': 'application/json',
       'Authorization': `user Bearer ${access_token}`
     },
     body: JSON.stringify({
       username: username,
       ...body,
     })
   });
   let data = await response.json();
   console.log(data);
   status = data.status;
   if (status == 22){
     return data;
   } else if (status == 14 || status == 15 || status == "null"){
     upd_tokens_status = await updateTokens();
     if (upd_tokens_status == 23){
        return makeRequest(func, body);
     }
   } else if (status == 31){
     return makeRequest(func, body);
   }
 } catch (error) {
   console.error('Error:', error);
 }
}


function logout(){
  window.location.href = "/logout/";
}
