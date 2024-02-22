//import Cookies from 'js-cookie';
import React, { useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';


function DropZone(){
  const [explorer, setExplorer] = React.useState([]);
  const [userFiles, setUserFiles] = React.useState([]);
  const [currdir, setCurrdir] = React.useState('root');
  const [isGetData, setIsGetData] = React.useState(false);
  const [files, setFiles] = React.useState([]);

  const onDrop = useCallback(acceptedFiles => {
    setFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  useEffect(() => {
      getUserData();
    }, []);

  useEffect(() => {
      changeDirectory();
      // eslint-disable-next-line
    }, [currdir]);

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
                <button className="file-remove-btn" onClick={() => removeFile(index)}>x</button>
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
	  {currdir !== "root" && <button className="prevFolder" onClick={() => {
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
	    ) : isGetData === true && currdir === "root" ? (
	      <h3>"Create your first folder or add a file!"</h3>
	    ) : isGetData === true && currdir !== "root" ? (
	      <h3>"Folder is empty"</h3>
	    ) : (
	      <h3>"Getting your data"</h3>
	    )}
	  </div>
     	</div>
    </div>
  );

			// <a href={`https://node2.whoole.space:8002/media/${window.username}/${item.name}`}>open {item.name}</a>
  
  function removeAllFiles(){
    setFiles([]);
  };


  function removeFile(index){
    const newFiles = [...files];
    newFiles.splice(index,  1);
    setFiles(newFiles);
  };


  function deleteItemByName(nameToRemove){
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


  async function uploadFiles(){
     let body = { "parent": currdir }
     files.forEach(file => {
	if (userFiles.some(item => item.name === file.name)){
     	  alert(`File or folder with name "${file.name}" already exists`);
     	  return;
	}
	let item = {
            'type': 'file',
            'name': file.name,
            'parent': currdir, 
            'date_added': file.lastModified,
	}
     	setUserFiles(prevUserFiles => [...prevUserFiles, item]);
     	setExplorer(prevExplorer => [...prevExplorer, item]);
     });
     const data = await window.makeRequest('UploadFiles', body, files)
     if (data.status == 25){
       data.existed_files.forEach(file => {
                deleteItemByName(file.name)
       })
       alert("We apologize, it didn't go as planned.")
     } else {
     setFiles([])
     }
  }


  async function downloadFiles(file_name){
     let body = {'file_name': file_name}
     const response = await window.makeRequest('DownloadFiles', body)
     let blob = await response.blob() 
     const url = window.URL.createObjectURL(blob);
     const a = document.createElement('a');
     a.style.display = 'none';
     a.href = url;
     a.download = file_name;
     document.body.appendChild(a);
     a.click();
     window.URL.revokeObjectURL(url);
  }
     //const access_token = Cookies.get('access_token');
     //fetch(`https://${window.node_domain}.whoole.space:8002/`, {
     //  method: 'GET',
     //  headers: {
     //    'Accept': '*',
     //    'Authorization': `user Bearer ${access_token}`,
     //    'username': window.username,
     //  },
     //})
     //.then(response => response.blob())
     //.then(blob => {
     //  const url = window.URL.createObjectURL(blob);
     //  const a = document.createElement('a');
     //  a.style.display = 'none';
     //  a.href = url;
     //  a.download = "script.js";
     //  document.body.appendChild(a);
     //  a.click();
     //  window.URL.revokeObjectURL(url);
     //})
     //.catch(error => console.error('Error:', error));


  async function createFolder(name){
     const exists = userFiles.some(item => item.name === name);
     if (exists) {
       alert(`File or folder with name "${name}" already exists`);
       return;
     }
     let item = {
        'name': name,
        'parent': currdir, 
        'type': 'folder',
     };

     setUserFiles(prevUserFiles => [...prevUserFiles, item]);
     setExplorer(prevExplorer => [...prevExplorer, item]);

     if (name === ""){
        alert("folder name must be a non-empty string");
        return;
     };
     let body = {
	'folder_name': name,
	'folder_parent': currdir,
     };
     const data = await window.makeRequest('CreateFolder', body);
     if (data.status !== 24){
        deleteItemByName(name)
	alert("We apologize, it didn't go as planned.")
     }
  };


  async function getUserData() {
    console.log('start getting data');
    let data = await window.makeRequest('GetUserData');
    if (data.status < 20) {
      console.log(data.msg, data.status);
      return;
    }
    setUserFiles(data.data);
    const rootFiles = data.data.filter(item => item.parent === "root");
    setExplorer(rootFiles);
    setIsGetData(true);
  }


  function changeDirectory(){
    console.log(files);
    let	newExplorer = userFiles.filter(item => item.parent === currdir);
    setExplorer(newExplorer)
    console.log(`set dir to ${currdir}`)
  }

};


export {DropZone};
