import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';


function DropZone(){
  const [explorer, setExplorer] = React.useState([]);
  const [currdir, setCurrdir] = React.useState('root');
  const [files, setFiles] = React.useState([]);

  const onDrop = useCallback(acceptedFiles => {
    console.log(acceptedFiles.map(file => file.name));
    setFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

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
	  <button onClick={getUserData}>test get user data</button>
	  <div className="xui">
            {explorer.length > 0 ? (explorer.map((item, index) => (
              <li key={index}>
                <h5>{item.name}</h5>
              </li>
            ))
	    ) : (
	       <h1>"Create your first folder or add a file!"</h1>
	    )}
	  </div>
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
     const exists = explorer.some(item => item.name === name);
     if (exists) {
       alert(`Folder with name "${name}" already exists`);
       return;
     }
     let item = {
        'name': name,
        'parent': currdir, 
        'type': 'folder',
     };

     setExplorer(prevExplorer => [...prevExplorer, item]);

     if (name === ""){
        alert("folder name must be a non-empty string");
        return;
     };
     let body = {
	'folder_name': name,
	'folder_parent': currdir,
     };
     window.makeRequest('CreateFolder', body);
  };


   async function getUserData(){
     console.log('start gettin data');
     let response = await window.makeRequest('GetUserData');
     if (response.status < 20){
	console.log(response.msg, response.status);
	return;
     };
     setExplorer(response.data);
  };

};


export {DropZone};
