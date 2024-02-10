import React, { useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
// import axios from "axios";


function DropZone(){
  const [files, setFiles] = React.useState([]);

  const onDrop = useCallback(acceptedFiles => {
    console.log(acceptedFiles.map(file => file.name));
    setFiles(acceptedFiles);
    main()
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
          <h4>Files</h4>
          <ul id="files-map">
            {files.map((file, index) => (
              <li key={file.path}>
                {file.name}
                <button class="file-remove-btn" onClick={() => removeFile(index)}>x</button>
              </li>
            ))}
          </ul>
        </aside>
	<button id="remove-all-files" onClick={removeAllFiles}>remove all files</button>
    </div>
  );

  function main(){
     window.mainFunc()
  }
  
  
  function removeAllFiles(){
    setFiles([]);
  };


  function removeFile(index){
    const newFiles = [...files];
    newFiles.splice(index,  1);
    setFiles(newFiles);
  };

};




export default DropZone;
