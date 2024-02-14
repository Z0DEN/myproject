import React, { useCallback, useEffect } from 'react';
import { useDropzone } from 'react-dropzone';


function DropZone(){
  const [explorer, setExplorer] = React.useState([]);
  const [userFiles, setUserFiles] = React.useState([]);
  const [currdir, setCurrdir] = React.useState('root');
  const [isGetData, setIsGetData] = React.useState(false);
  const [files, setFiles] = React.useState([]);

  const onDrop = useCallback(acceptedFiles => {
    console.log(acceptedFiles.map(file => file.name));
    setFiles(acceptedFiles);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({ onDrop });

  useEffect(() => {
      getUserData();
    }, []);

  useEffect(() => {
      changeDirectory(); //func which modify explorer depending on currdir
	  // eslint-disable-next-line
    }, [currdir]);

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
	  {currdir !== "root" && <button className="prevFolder" onClick={() => {
	     let prevFolder = userFiles.filter(item => item.name === currdir)
	     console.log(prevFolder.parent)
	  }}>prev</button>}
	  <div className="explorer">
	    {explorer.length > 0 ? (
	      explorer.map((item, index) => (
	          <button className="explorer-item" key={index} onClick={() => setCurrdir(item.name)}>
	            {item.name}
	          </button>
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


  async function createFolder(name){
     const exists = userFiles.some(item => item.name === name);
     if (exists) {
       alert(`Folder with name "${name}" already exists`);
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
     let data = await window.makeRequest('CreateFolder', body);
     if (data.status !== 24){
        deleteItemByName(name)
	alert("We apologize, it didn't go as planned.")
     }
  };


  async function getUserData(){
     console.log('start gettin data');
     let response = await window.makeRequest('GetUserData');
     if (response.status < 20){
	console.log(response.msg, response.status);
	return;
     };
     setUserFiles(response.data);
     const rootFiles = response.data.filter(item => item.parent === "root");
     setExplorer(rootFiles)
     setIsGetData(true)
  };

  function changeDirectory(){
    let	newExplorer = userFiles.filter(item => item.parent === currdir);
    setExplorer(newExplorer)
    console.log(`new dir is ${currdir}`)
  }

};


export {DropZone};
