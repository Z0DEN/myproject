import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
// import axios from "axios";

function DropZone(){
  const [currdir, setCurrdir] = React.useState('root' || []);
  const [files, setFiles] = React.useState([]);

  const onDrop = useCallback(acceptedFiles => {
    console.log(acceptedFiles.map(file => file.name));
    setFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  window.getUserData = getUserData()

  return (
    <div>
      <div {...getRootProps()} id="drop-zone">
        <input {...getInputProps()} />
        {isDragActive ? (
          <h3>Drop the files here ...</h3>
        ) : (
          <h3>Drag 'n' drop some files here, or click to select files</h3>
        )}
      </div>
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
	      <button id="remove-all-files" onClick={removeAllFiles}>remove all files</button>
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
     	</div>
    </div>
  );

  
  function removeAllFiles(){
    setFiles([]);
  };


  function removeFile(index){
    const newFiles = [...files];
    newFiles.splice(index,  1);
    setFiles(newFiles);
  };


  function createFolder(name){
     if (name === ""){
        alert("folder name must be a non-empty string");
        return;
     }
     let body = {
	'folder_name': name,
	'folder_parent': currdir,
     }
     window.makeRequest('CreateFolder', body)
  }


  function getUserData(){
   console.log('start gettin data')
   let data = makeRequest('GetUserData')
   console.log(data)
  }
};


export {DropZone};
