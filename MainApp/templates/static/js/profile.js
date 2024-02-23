const csrf_cookie = Cookies.get('csrftoken')
let access_token;
let response_data;


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


async function makeRequest(func='GetUserData', body={}, files=[]) {
 access_token = Cookies.get('access_token');
 let bodyData;
 let headers = {
       'Authorization': `user Bearer ${access_token}`,
       'username': username, 
     };

 if (files.length > 0){  
     var formData = new FormData();
     for (let i = 0; i < files.length; i++){
        formData.append('user_files', files[i]);
     }
     for (let key in body) {
         formData.append(key, body[key]);
     }
     formData.append('username', username);
     bodyData = formData;
     console.log(bodyData);
  } else{
     console.log(body)
     bodyData = JSON.stringify({
       username: username,
       ...body,
     })
  };

 try {
   let response = await fetch(`https://${node_domain}.whoole.space:8002/${func}/`, {
     method: 'POST',
     headers: headers,
     body: bodyData,
   });
   const contentType = await response.headers.get('Content-Type')
   console.log(contentType)
   data = await response.json()
   console.log(data)
   status = data.status 
   if (status == 14 || status == 15 || status == "null"){
     upd_tokens_status = await updateTokens();
     if (upd_tokens_status > 20){
        return await makeRequest(func, body, files);
     }
   } else if (status == 31){
     return await makeRequest(func, body, files);
   } else {
     return data;
   }
 } catch (error) {
   console.error('Error:', error);
 }
}


function logout(){
  window.location.href = "/logout/";
}
