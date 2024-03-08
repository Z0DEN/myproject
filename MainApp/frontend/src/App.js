//import Cookies from 'js-cookie';
import { v4 as uuidv4 } from 'uuid';
import React, { useCallback, useEffect, useState} from 'react';
import { useDropzone } from 'react-dropzone';


function DropZone(){
  const [explorer, setExplorer] = useState([]);
  const [userFiles, setUserFiles] = useState([]);
  const [files, setFiles] = useState([]);
  const [currdir, setCurrdir] = useState(null);
  const [isGetData, setIsGetData] = useState(false);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationText, setNotificationText] = useState('');

  const Notification = useCallback((text) => {
    if (text && showNotification === false){
	setNotificationText(text);
        setShowNotification(true);
        const timer = setTimeout(() => {
          setShowNotification(false);
        }, 3000);
        return () => {
          clearTimeout(timer);
        };
    } else{ 
       return;
    }
  }, [showNotification]);


  async function createFolder(name){
     if (name === ""){
        Notification("folder name must be a non-empty string");
        return;
     }

     const exists = userFiles.some(item => item.name === name && item.parent_id[0] === currdir);
     if (exists) {
       Notification(`File folder with name "${name}" already exists`);
       return;
     }

     let item_id = uuidv4();
     const d = new Date();
     
     let item = {
        'type': 'folder',
        'name': name,
	'item_id': item_id,
        'parent_id': [currdir], 
	'data_added': d.toISOString(),
     };

     setUserFiles(prevUserFiles => [...prevUserFiles, item]);
     setExplorer(prevExplorer => [...prevExplorer, item]);

     let body = {
	'folder_name': name,
	'item_id': item_id,
	'parent_id': currdir,
     };
     const data = await window.makeRequest('CreateFolder', body);
     try{
       if (data.status !== 24){
          deleteItemFromFiles(item_id)
          Notification(data.msg)
       }
       Notification(`Created folder "${name}"`)
     } catch(error){
        deleteItemFromFiles(item_id)
	console.log(error)
     }
  };

  
  async function deleteItem(item_id, type, name){
     let body = {'item_id': item_id, 'item_type': type}
     const data = await window.makeRequest('DeleteItem', body)
     try{
       if (data.status === 20){
          deleteItemFromFiles(item_id)
          Notification(`Delete item "${name}"`)
       }
       if (data.status === 10){
          Notification('Error occurs while deleting')
       }
     } catch(error) {
	console.log(error)
     }
  }


  async function uploadFiles(){
     if (files.length > 0){
       var filesToUpload = [];
       var body = { 'parent_id': currdir }
       for (let i=0; i < files.length; i++) {
	 let file_item = files[i];
         if (userFiles.some(item => item.name === file_item.file.name && item.parent_id[0] === currdir)){
       	   Notification(`File or folder with name "${file_item.file.name}" already exists`);
           continue;
         }
	 body[file_item.file.name] = file_item.item_id;
         let item = {
             'type': 'file',
             'name': file_item.file.name,
	     'item_id': file_item.item_id,
             'parent_id': [currdir],
             'date_added': file_item.file.lastModified,
         };
       	 setUserFiles(prevUserFiles => [...prevUserFiles, item]);
       	 setExplorer(prevExplorer => [...prevExplorer, item]);
	 filesToUpload.push(file_item.file);
       };
     } else{
       console.log('files is empty')
     }
     const data = await window.makeRequest('UploadFiles', body, filesToUpload)
     try{
       if (data.status === 25){
         Notification("Upload is done")
       } else if(data.status === 18){
	 Notification(data.msg)
	 files.forEach(file_item => {
	   deleteItemFromFiles(file_item.item_id)
	 });
       } else if (data.status === 13){
         const foundFolder = userFiles.find(item => item.item_id === currdir).name
         Notification(`Folder ${foundFolder} does not exists`)
	 files.forEach(file_item => {
	   deleteItemFromFiles(file_item.item_id)
	 });
       }
     } catch(error){
	console.log(error)
	files.forEach(file_item =>{
	  deleteItemFromFiles(file_item.item_id)
	});
     }
     setFiles([])
  }


  async function downloadFiles(item_id, file_name){
     let body = {'item_id': item_id}
     try{
     const response = await window.makeRequest('DownloadFiles', body)
     let blob = await response.blob() 
	 console.log(blob)
     const url = window.URL.createObjectURL(blob);
     const a = document.createElement('a');
     a.style.display = 'none';
     a.href = url;
     a.download = file_name;
     document.body.appendChild(a);
     a.click();
     window.URL.revokeObjectURL(url);
     } catch(error){
         console.log(error)
     } 
  }


  const getUserData = useCallback(async () => {
    console.log('start getting data');
    try {
      let data = await window.makeRequest('GetUserData');
      if (data.status < 20) {
        console.log(data.msg, data.status);
        return;
      }
      setUserFiles(data.data);
      const rootFiles = data.data.filter(item => item.parent_id.includes(null));
      setExplorer(rootFiles);
      setIsGetData(true);
    } catch (error) {
      console.log(error);
      Notification("Error occurs while getting your data");
    }
  }, [Notification]);


  useEffect(() => {
    getUserData();
  }, []);


  const changeDirectory = useCallback(async () => {
    let	newExplorer = await userFiles.filter(item => item.parent_id.includes(currdir));
    setExplorer(newExplorer);
//    const foundItem = userFiles.find(item => item.item_id === currdir);
//    if (foundItem){
//      console.log(`set dir to`, foundItem.name)
//    }
  }, [currdir]);


  useEffect(() => {
      changeDirectory();
    }, [currdir, changeDirectory]);


  const onDrop = useCallback(acceptedFiles => {
      const filesWithItemId = acceptedFiles.map(file => ({
          file: file,
          item_id: uuidv4(),
      }));
      setFiles(filesWithItemId);
  }, []);


  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
      <>
	<div className="explorer">
	  {explorer.length > 0 ? (
	    explorer.map((item, index) => (
	        item.type === "folder" ? (
		     <div key={item.item_id || index} className="folder-item">
		        <span className="folder-name">
			   <img width="48" height="48" src="https://whoole.space/static/images/folder-icon.svg" alt="folder-invoices--v1"/>
		 	   <button className="explorer-folder" key={index} onClick={() => setCurrdir(item.item_id)}>{item.name}</button>
			</span>
		        <span className="folder-options">
		           <button onClick={() => deleteItem(item.item_id, 'folders', item.name)} className="delete-folder">Удалить</button>
			</span>
		     </div>
		) : (
		 <div key={item.id || index} className="file-item">
		   <span className="file-name">
   		     <img 
			width="48" 
			height="48" 
			src={`https://whoole.space/static/images/${window.existExt.hasOwnProperty(getFileExtension(item.name)) ? window.existExt[getFileExtension(item.name)] : "undefined-file-icon.svg"}`} 
			alt="file"/>
	             <h5 className={`explorer-file ${getFileExtension(item.name)}`}>{item.name}</h5>
		   </span>
		   <span className="file-options">
	      	     <button className="download-file" onClick={() => {
	      	           downloadFiles(item.item_id, item.name)
	      	     }}>Скачать</button>
		     <button onClick={() => deleteItem(item.item_id, 'files', item.name)} className="delete-file">Удалить</button>
		   </span>
		 </div>
	         )
	    ))
	  ) : isGetData === true && currdir === null ? (
	    <h1 className="message">Create your first folder or add a file!</h1>
	  ) : isGetData === true && currdir !== null ? (
	    <h1 className="message">Folder is empty</h1>
	  ) : (
	    <h1 className="message">Getting your data</h1>
	  )}

	  {currdir !== null && <button id="prev-btn" onClick={() => {
             let foundItem = userFiles.find(item => item.item_id === currdir);
             let prevFolder = foundItem ? foundItem.parent_id[0] : null;
	     setCurrdir(prevFolder)
	  }}><svg id="prev-btn-icon" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#000000" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M10 16l-6-6 6-6"/><path d="M20 21v-7a4 4 0 0 0-4-4H5"/></svg></button>}
	</div>
	  

  	<div className="options">
	  <div className="user-info">
	    <h1>{window.username}</h1>
            <button onClick={() => window.logout()} id="logout-btn">Logout</button>
	  </div>

          <div className="drop-zone-container">
            {files.length === 0 && <div {...getRootProps()} id="drop-zone">
              <input {...getInputProps()} />
              {isDragActive ? (
                <h3>Drop the files here ...</h3>
              ) : (
                <h3>Drag 'n' drop some files here, or click to select files</h3>
              )}
            </div>}

	  {files.length > 0 && 
	    <ul id="files-map">
              {files.map((file_item, index) => (
                <span key={file_item.file.path} className="input-file-item">
                  <svg className="file-remove-btn" onClick={() => removeFileFromInput(index)} xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="1 1 22 22" fill="none" stroke="#e25656" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
                  <h5>{file_item.file.name}</h5>
                </span>
              ))}
            </ul>}
          </div>

	  { files.length > 0 &&(
	     <>
	      <button id="upload-files" onClick={uploadFiles}>upload files</button>
	      <button id="remove-all-files" onClick={removeAllFiles}>remove all files</button>
	     </>
	  )}
	
     	  <input
     	    type="text"
     	    id="folder-input"
     	    name="folder"
     	    placeholder="enter a folder name"
	    disabled={!isGetData}
     	    onKeyDown={event => {
     	      if (event.key === 'Enter') {
     	        event.preventDefault();
     	        createFolder(event.target.value);
     	      }
     	    }}
     	  />

	  <div className="file-info"></div>

          {showNotification && <h3 className="Notification">{notificationText}</h3>}
     	</div>
      </>	
  );

// <a href={`https://node2.whoole.space:8002/media/${window.username}/${item.name}`}>open {item.name}</a>

  function removeAllFiles(){
    setFiles([]);
  };


  function removeFileFromInput(index){
    const newFiles = [...files];
    newFiles.splice(index,  1);
    setFiles(newFiles);
  };


  function deleteItemFromFiles(ItemIdToRemove){
    setUserFiles((currentFiles) => {
      return currentFiles.filter((item) => item.item_id !== ItemIdToRemove);
    });
    setExplorer((currentFiles) => {
      return currentFiles.filter((item) => item.item_id!== ItemIdToRemove);
    });
  };


  function getFileExtension(filename) {
    return filename.toLowerCase().substring(filename.lastIndexOf('.') +  1);
  }

};


export {DropZone};
