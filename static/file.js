// Check for the various File API support.
if (window.File && window.FileReader && window.FileList && window.Blob) {
  // Great success! All the File APIs are supported.
} else {
  alert('The File APIs are not fully supported in this browser.');
}

function handleFileSelect(evt) {
    if (evt.type == 'change') {
        var files = evt.target.files; // FileList object
    } else if (evt.type =='drop') {
        evt.stopPropagation();
        evt.preventDefault();
        var files = evt.dataTransfer.files; // FileList object.   
    }    
    // files is a FileList of File objects. List some properties.
    var output = [];
    for (var i = 0, f; f = files[i]; i++) {
        output.push('<li><strong>', escape(f.name), '</strong> (', f.type || 'n/a', ') - ',
                    f.size, ' bytes, last modified: ',
                    f.lastModifiedDate ? f.lastModifiedDate.toLocaleDateString() : 'n/a',
                    '</li>');
		Encrypt(f);
    }
	document.getElementById('list').innerHTML = '<ul>' + output.join('') + '</ul>';    
}


function Encrypt(file) {
    var reader = new FileReader();
	reader.readAsText(file);
    reader.onload = function (e) {
          	if (reader.error) { 
				 console.log(reader.error); 
			} else { 
				var urlData = this.result;
				//document.getElementById("result").innerHTML +=urlData;
				var password=document.getElementById("userkey").value;
				var encrypted = sjcl.encrypt(password, urlData);
				var dencrypted = sjcl.decrypt(password, encrypted);
				//console.log(urlData);
				//console.log(encrypted);
				//console.log(dencrypted);
				var blob = new Blob([dencrypted], { type: "\""+file.type+"\"" });
			    console.log(blob.size);  
				//console.log(blob.name);
			    console.log(blob.type);
				//upload(f.name,encrypted);

			}
    }; 
}

function uploadfiles(file,encrypted) {
	var xhr = new XMLHttpRequest();

    xhr.upload.addEventListener("progress", uploadProgress, false);
    xhr.addEventListener("load", uploadComplete, false);
    xhr.addEventListener("error", uploadFailed, false);
    xhr.addEventListener("abort", uploadCanceled, false);

	xhr.open("POST", "https://sefss.s3.amazonaws.com/?fileName=" + file.name);
	xhr.overrideMimeType("application/octet-stream");
	xhr.sendAsBinary(encrypted);
	xhr.onreadystatechange = function() {
		if (xhr.readyState == 4) {
			if (xhr.status == 200) {
				console.log("upload complete");
				console.log("response: " + xhr.responseText);
			}
		}
	}
 
}

      function uploadProgress(evt) {
        if (evt.lengthComputable) {
          var percentComplete = Math.round(evt.loaded * 100 / evt.total);
          document.getElementById('progressNumber').innerHTML = percentComplete.toString() + '%';
        }
        else {
          document.getElementById('progressNumber').innerHTML = 'unable to compute';
        }
      }

      function uploadComplete(evt) {
        /* This event is raised when the server send back a response */
        alert(evt.target.responseText);
      }

      function uploadFailed(evt) {
        alert("There was an error attempting to upload the file.");
      }

      function uploadCanceled(evt) {
        alert("The upload has been canceled by the user or the browser dropped the connection.");
      }


function handleDragOver(evt) {
    evt.stopPropagation();
    evt.preventDefault();
    evt.dataTransfer.dropEffect = 'copy'; // Explicitly show this is a copy.
}

document.getElementById('file').addEventListener('change', handleFileSelect, false);
var dropZone = document.getElementById('drop_zone');
dropZone.addEventListener('dragover', handleDragOver, false);
dropZone.addEventListener('drop', handleFileSelect, false);
