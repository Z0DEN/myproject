//import Cookies from 'js-cookie';
import { v4 as uuidv4 } from 'uuid';
import React, { useCallback, useEffect, useState, useRef} from 'react';
import { useDropzone } from 'react-dropzone';


function DropZone(){
  const [explorer, setExplorer] = useState([]);
  const [userFiles, setUserFiles] = useState([]);
  const [files, setFiles] = useState([]);
  const [currdir, setCurrdir] = useState(null);
  const [isGetData, setIsGetData] = useState(false);
  const [notifications, setNotifications] = useState([]);
  const [filesTotalSize, setFilesTotalSize] = useState(0);
  const [takenSpace, setTakenSpace] = useState(0);
  const spaceLineRef = useRef(null);


  const Notification = (text) => {
    if (text !== ''){ 
	setNotifications(prevNotifications => [...prevNotifications, text.toString()]);
        const timer = setTimeout(() => {
	   setNotifications(prevNotifications => [...prevNotifications.filter(note => note !== text)])
        }, 10000);
        return () => {
          clearTimeout(timer);
        };
    } else{ 
       return;
    }
  };


  async function createFolder(name){
     if (name === ""){
        Notification("Имя папки не должно быть пустым");
        return;
     }

     const exists = userFiles.some(item => item.name === name && item.parent_id[0] === currdir);
     if (exists) {
       Notification(`Файл или папка с именем "${name}" уже существует`);
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
       Notification(`Создана папка: "${name}"`)
     } catch(error){
        deleteItemFromFiles(item_id)
	console.log(error)
     }
  };

  
  async function deleteItem(item_id, type, name, size=null){
     let confirmation = window.confirm('Подтвердите удаление...');
     if (!confirmation){
	return;
     }

     if (type === 'folders'){
	var totalSize = userFiles.reduce((acc, currentItem) => {
	   if (currentItem.parent_id.includes(item_id)){
	      return acc + currentItem.size;
	   }
	   return acc;
	}, 0);
     }

     let body = {'item_id': item_id, 'item_type': type};
     const data = await window.makeRequest('DeleteItem', body);
     try{
       if (data.status === 20){
          deleteItemFromFiles(item_id);
          Notification(`Удалено: "${name}"`);
          setTakenSpace(prevTakenSpace => prevTakenSpace - (size ? size : totalSize));
       }
       if (data.status === 10){
          Notification('Возникла ошибка при удалении');
       }
     } catch(error) {
	console.log(error);
     }
  }


  async function uploadFiles(){
     if (files.length > 0){
       if (filesTotalSize + takenSpace > window.availableSpace){
	  console.log(filesTotalSize + takenSpace)
	  Notification('Размер файлов > доступного места')
	  return
       }
       var filesToUpload = [];
       var body = { 'parent_id': currdir }
       for (let i=0; i < files.length; i++) {
	 let file_item = files[i];
         if (userFiles.some(item => item.name === file_item.file.name && item.parent_id.includes(currdir))){
       	   Notification(`Файл или папка с именем: "${file_item.file.name}" уже существует`);
           continue;
         }
	 body[file_item.file.name] = file_item.item_id;
         let item = {
             'type': 'file',
             'name': file_item.file.name,
	     'item_id': file_item.item_id,
             'parent_id': [currdir],
             'date_added': file_item.file.lastModified,
	     'size': file_item.file.size,
         };
       	 setUserFiles(prevUserFiles => [...prevUserFiles, item]);
       	 setExplorer(prevExplorer => [...prevExplorer, item]);
	 filesToUpload.push(file_item.file);
       };
     } else{
       console.log('files is empty')
     }
     if (filesToUpload.length === 0) {
	return;
     }
     Notification("Файлы загружаются, не выходите")
     const data = await window.makeRequest('UploadFiles', body, filesToUpload)
     try {
	switch(data.status) {
	   case 25:
         	Notification("Загрузка завершена");
	 	setTakenSpace(prevTakenSpace => prevTakenSpace + filesTotalSize);
    	 	setFiles([]);
		break;
	   case 19:
	 	Notification(data.msg)
	 	return
	   case 18:
	 	Notification(data.msg);
	 	files.forEach(file_item => {
	 	  deleteItemFromFiles(file_item.item_id)
	 	});
		break;
	   case 13:
         	const foundFolder = userFiles.find(item => item.item_id === currdir).name
         	Notification(`Папка ${foundFolder} не существует`)
	 	files.forEach(file_item => {
	 	  deleteItemFromFiles(file_item.item_id)
	 	});
		break;
	}
     } catch(error){
	Notification('Ошибка: возможно размер файлов слишком большой')
	files.forEach(file_item =>{
	  deleteItemFromFiles(file_item.item_id)
	});
     }
//     try{
//       if (data.status === 25){
//         Notification("Загрузка завершена")
//	 setTakenSpace(prevTakenSpace => prevTakenSpace + filesTotalSize);
//    	 setFiles([])
//       } else if(data.status === 19){
//	 Notification(data.msg)
//	 return
//       } else if(data.status === 18){
//	 Notification(data.msg)
//	 files.forEach(file_item => {
//	   deleteItemFromFiles(file_item.item_id)
//	 });
//       } else if (data.status === 13){
//         const foundFolder = userFiles.find(item => item.item_id === currdir).name
//         Notification(`Папка ${foundFolder} не существует`)
//	 files.forEach(file_item => {
//	   deleteItemFromFiles(file_item.item_id)
//	 });
//       }
//     } catch(error){
//	Notification('Ошибка: возможно размер файлов слишком большой')
//	files.forEach(file_item =>{
//	  deleteItemFromFiles(file_item.item_id)
//	});
//     }
  }


  async function downloadFiles(item_id, file_name){
     let body = {'item_id': item_id}
     try{
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
      setTakenSpace(data.taken_space);
      window.availableSpace = data.available_space;

      const rootFiles = data.data.filter(item => item.parent_id.includes(null));
      setExplorer(rootFiles);
      setIsGetData(true);
    } catch (error) {
      console.log(error);
      Notification("Возникла ошибка при получении данных");
    }
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
    getUserData();
  }, []);


  useEffect(() => {
      changeDirectory();
    }, [currdir, changeDirectory]);


  useEffect(() => {
      const totalSize = files.reduce((acc, file_item) => acc + file_item.file.size, 0);
      setFilesTotalSize(totalSize);
    }, [files]);

  
  useEffect(() => {
   let percent = takenSpace / window.availableSpace * 100;
   let backColor = percent < 50 ? 'green' : percent < 90 ? 'orange' : 'red';
   if (spaceLineRef.current) {
      spaceLineRef.current.style.setProperty('--before-width', `${percent}%`);
      spaceLineRef.current.style.setProperty('--before-back-color', `${backColor}`);
   }
  }, [takenSpace]);


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
	      	     }}>Скачать {formatSizeUnits(item.size)}</button>
		     <button onClick={() => deleteItem(item.item_id, 'files', item.name, item.size)} className="delete-file">Удалить {formatSizeUnits(item.size)}</button>
		   </span>
		 </div>
	         )
	    ))
	  ) : isGetData === true && currdir === null ? (
            <h1 className="message">Создайте свою первую папку или добавьте файл!</h1>
	  ) : isGetData === true && currdir !== null ? (
            <h1 className="message">Папка пуста</h1>
	  ) : (
            <h1 className="message">Получение данных</h1>
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
	     <span id="space" ref={spaceLineRef}>
	       <h3>{formatSizeUnits(takenSpace)}/{formatSizeUnits(window.availableSpace)}</h3>
	       <span id="space-line"></span>
	     </span>
             <button onClick={() => window.logout()} id="logout-btn">Выйти</button>
	  </div>

          <div className="drop-zone-container">
            {files.length === 0 && <div {...getRootProps()} id="drop-zone">
              <input {...getInputProps()} />
              {isDragActive ? (
		<h3>Добавить выбранные файлы...</h3>
              ) : (
                <h3>Перетащите сюда файлы или кликните, чтобы выбрать</h3>
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
              <button id="upload-files" onClick={uploadFiles}>Загрузить {formatSizeUnits(filesTotalSize)}</button>
              <button id="remove-all-files" onClick={removeAllFiles}>Очистить всё</button>
	     </>
	  )}
	
     	  <input
     	    type="text"
     	    id="folder-input"
     	    name="folder"
     	    placeholder="Введите название папки"
	    disabled={!isGetData}
     	    onKeyDown={event => {
     	      if (event.key === 'Enter') {
     	        event.preventDefault();
     	        createFolder(event.target.value);
     	      }
     	    }}
     	  />

	  {notifications.length > 0 && (
	    <div id="Notification-div">
	        <ul className="Notification">
	          {notifications.map((notification, index) => (
	            <li key={index}>{notification}</li>
	          ))}
	        </ul>
	    </div>
	  )}

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


  function formatSizeUnits(bytes) {
   if (bytes >= 1073741824) {
      return (bytes / 1073741824).toFixed(2) + " GB";
   } else if (bytes >= 1048576) {
      return (bytes / 1048576).toFixed(2) + " MB";
   } else if (bytes >= 1024) {
      return (bytes / 1024).toFixed(2) + " KB";
   } else if (bytes > 1) {
      return bytes + " bytes";
   } else if (bytes === 1) {
      return bytes + " byte";
   } else {
      return "0";
   }
  }

};


export {DropZone};
