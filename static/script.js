//convert text to speech
const {readFileSync, promises: fsPromises} = require('fs');

function readFile(filePath) {
    return new Promise((resolve, reject) => {
        fsPromises.readFile(filePath)
            .then(data => resolve(data))
            .catch(err => reject(err));
    });
}

function speak() {
    // console.log("speak");
    //get the text from the textarea
    //read a file that ends with .txt
    file_dir = "static/uploads/";
    file_ext = ".txt";
    $.ajax({
        //This will retrieve the contents of the folder if the folder is configured as 'browsable'
        url: file_dir,
        success: function (data) {
            // read the file that ends with .txt

            $(data).find("a:contains(" + fileextension + ")").each(function () {
                var filename = this.href.replace(window.location.host, "").replace("http:///", "");   
            });
            console.log(filename);

        }
    });
    
    var text = document.getElementById("text").value;
    console.log(text);
    var msg = new SpeechSynthesisUtterance(text);
    window.speechSynthesis.speak(msg);
}

speak();