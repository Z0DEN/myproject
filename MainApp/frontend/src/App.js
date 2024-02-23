//import Cookies from 'js-cookie';
import React, { useCallback, useEffect, useState} from 'react';
import { useDropzone } from 'react-dropzone';


function DropZone(){
  const [explorer, setExplorer] = useState([]);
  const [userFiles, setUserFiles] = useState([]);
  const [currdir, setCurrdir] = useState(null);
  const [isGetData, setIsGetData] = useState(false);
  const [files, setFiles] = useState([]);
  const [showNotification, setShowNotification] = useState(false);
  const [notificationText, setNotificationText] = useState('');


  const Notification = useCallback((text) => {
    if (text && showNotification === false){
	setNotificationText(text);
        setShowNotification(true);
        const timer = setTimeout(() => {
          setShowNotification(false);
        }, 5000);
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

     const exists = userFiles.some(item => item.name === name && item.parent === currdir);
     if (exists) {
       Notification(`File folder with name "${name}" already exists`);
       return;
     }
     let item = {
        'name': name,
        'parent': currdir, 
        'type': 'folder',
     };

     setUserFiles(prevUserFiles => [...prevUserFiles, item]);
     setExplorer(prevExplorer => [...prevExplorer, item]);

     let body = {
	'folder_name': name,
	'folder_parent': currdir,
     };
     const data = await window.makeRequest('CreateFolder', body);
     if (data.status === 18){
        deleteItemFromUserFiles(name)
        Notification(data.msg)
     }
     Notification(`Created folder "${name}"`)
  };


  async function uploadFiles(){
     let body = { "parent": currdir }
     if (files.length > 0){
       for (let i=0; i < files.length; i++) {
	 let file = files[i];
         if (userFiles.some(item => item.name === file.name && item.parent === currdir)){
       	   Notification(`File or folder with name "${file.name}" already exists`);
           removeFileFromInput(file.name);
           continue;
         }
         let item = {
             'type': 'file',
             'name': file.name,
             'parent': currdir, 
             'date_added': file.lastModified,
         };
       	 setUserFiles(prevUserFiles => [...prevUserFiles, item]);
       	 setExplorer(prevExplorer => [...prevExplorer, item]);
       };
     } else{
       console.log('files is empty')
     }
     const data = await window.makeRequest('UploadFiles', body, files)
     try{
       setFiles([])
       if (data.status === 18){
         Notification(`These files already exists: ${data.existed_files.join(', ')}`)
	 data.existed_files.forEach(name =>{
	   deleteItemFromUserFiles(name)
	 });
       } else if (data.status === 13){
	 Notification(data.msg)
       } else {
         Notification("Upload is done")
       }
     } catch(error){
	console.log(error)
     }
  }


  async function downloadFiles(file_name){
     let body = {'file_name': file_name}
     const response = await window.makeRequest('DownloadFiles', body)
//     const jsonString = JSON.stringify(response);
//     const blob = new Blob([jsonString], {type: "application/json"});
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
  }


  const getUserData = useCallback(async () => {
    console.log('start getting data');
    try {
      let data = await window.makeRequest('GetUserData');
      if (data.status <  20) {
        console.log(data.msg, data.status);
        return;
      }
      setUserFiles(data.data);
      const rootFiles = data.data.filter(item => item.parent === null);
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


  const changeDirectory = useCallback(() => {
    let	newExplorer = userFiles.filter(item => item.parent === currdir);
    setExplorer(newExplorer)
    console.log(`set dir to ${currdir}`)
  }, [currdir]);


  useEffect(() => {
      changeDirectory();
    }, [currdir, changeDirectory]);


  const onDrop = useCallback(acceptedFiles => {
    setFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  return (
    <div>
      {files.length === 0 && <div {...getRootProps()} id="drop-zone">
        <input {...getInputProps()} />
        {isDragActive ? (
          <h3>Drop the files here ...</h3>
        ) : (
          <h3>Drag 'n' drop some files here, or click to select files</h3>
        )}
      </div>}
        <aside>
          <ul id="files-map">
            {files.map((file, index) => (
              <li key={file.path}>
                <button className="file-remove-btn" onClick={() => removeFileFromInput(index)}>x</button>
                <h5>{file.name}</h5>
              </li>
            ))}
          </ul>
        </aside>
	  { files.length > 0 &&(
	     <>
	      <button id="remove-all-files" onClick={removeAllFiles}>remove all files</button>
	      <button id="upload-files" onClick={uploadFiles}>upload files</button>
	     </>
	  )}
     	<div>
     	  <input
     	    type="text"
     	    id="folder-input"
     	    name="folder"
     	    placeholder="enter a folder name"
     	    onKeyDown={event => {
     	      if (event.key === 'Enter') {
     	        event.preventDefault();
     	        createFolder(event.target.value);
     	      }
     	    }}
     	  />
	  {currdir !== null && <button className="prevFolder" onClick={() => {
             let foundItem = userFiles.find(item => item.name === currdir);
             let prevFolder = foundItem ? foundItem.parent : null;
	     setCurrdir(prevFolder)
	  }}>prev</button>}
	  <div className="explorer">
	    {explorer.length > 0 ? (
	      explorer.map((item, index) => (
	          item.type === "folder" ? (<button className="explorer-folder" key={index} onClick={() => setCurrdir(item.name)}>{item.name}</button>)
		   :(<span key={item.id || index}>
		         <h5 className={`explorer-file ${getFileExtension(item.name)}`}>{item.name}</h5>
			 <button className="download-files" onClick={() => {
				 downloadFiles(item.name)
			 }}>*</button>
	  	     </span>
		   )
	      ))
	    ) : isGetData === true && currdir === null ? (
	      <h3>"Create your first folder or add a file!"</h3>
	    ) : isGetData === true && currdir !== null ? (
	      <h3>"Folder is empty"</h3>
	    ) : (
	      <h3>"Getting your data"</h3>
	    )}
	  </div>
	    {showNotification && <h3 className="Notification">{notificationText}</h3>}
     	</div>
    </div>
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


  function deleteItemFromUserFiles(nameToRemove){
    setUserFiles((currentFiles) => {
      return currentFiles.filter((item) => item.name !== nameToRemove);
    });
    setExplorer((currentFiles) => {
      return currentFiles.filter((item) => item.name !== nameToRemove);
    });
  };


  function getFileExtension(filename) {
    return filename.substring(filename.lastIndexOf('.') +  1);
  }

};


export {DropZone};
