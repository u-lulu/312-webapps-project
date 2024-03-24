
function dicePost(){
	const request = new XMLHttpRequest();
	request.onreadystatechange = function ()  {
		if (this.readyState === 4 && this.status == 200) {
		  console.log(this.response)
		}
	  };
	  request.open('POST', "/dice-post");
	  var formData = new FormData(document.getElementById("/dice-post")); 
	  console.log(formData);
	  request.send(formData);
	}

	
function textPost(){

	const request = new XMLHttpRequest();
	//const textPost = document.getElementById("body_text")
	//const txtMsg = textPost.value
	//textPost.value = "";

	request.onreadystatechange = function ()  {
		if (this.readyState === 4 && this.status == 200) {
			console.log(this.response)
		}
	};
	request.open('POST', "/text-post");
	var formData = new FormData(document.getElementById("/text-post")); 
	console.log(formData);
	request.send(formData);

}

function getPost(){
    //const request = new XMLHttpRequest();
	//const textPost = document.getElementById("body_text")
	//const txtMsg = textPost.value
	//textPost.value = "";

    request.onreadystatechange = function () {
        if (this.readyState === 4 && this.status == 200) {
			console.log(this.response)
        }
    }

	request.open("GET", "/posts")
    var formData = new FormData(document.getElementById("/posts")); 
	console.log(formData);
	request.send(formData);
}

function getOnePost() {
    const request = new XMLHttpRequest();
    request.onreadystatechange = function () {
        if (request.readyState === 4) {
            const messages = JSON.parse(this.response);
            for (const message of messages) {
                addMessageToChat(message);
            }
        }
    }

	request.open("GET", "/posts/<id>");
    var formData = new FormData(document.getElementById("/posts/<id>")); 
	console.log(formData);
	request.send(formData);
	
}