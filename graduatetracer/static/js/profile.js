// // //declearing html elements

 const imgDiv = document.querySelector('.image-field');
 const img = document.querySelector('#photo');
 const file = document.querySelector('#file');
 const uploadBtn = document.querySelector('#uploadBtn');

 //if user hover on img div

 imgDiv.addEventListener('mouseenter', function() {
    uploadBtn.style.display = "block";
});

 //if we hover out from img div

 imgDiv.addEventListener('mouseleave', function() {
    uploadBtn.style.display = "none";
 });

 //lets work for image showing functionality when we choose an image to upload

 //when we choose a foto to upload

file.addEventListener('change', function() {
     //this refers to file
     const choosedFile = this.files[0];

   if (choosedFile) {

        const reader = new FileReader(); //FileReader is a predefined function of JS
       reader.addEventListener('load', function() {
             img.setAttribute('src', reader.result);
        });

         reader.readAsDataURL(choosedFile);

       
    }
 });
 function myFunction() {
  var dots = document.getElementById("dots");
  var moreText = document.getElementById("more");
  var btnText = document.getElementById("btn");

  if (dots.style.display === "none") {
    dots.style.display = "inline";
    btnText.innerHTML = "Read more"; 
    moreText.style.display = "none";
  } else {
    dots.style.display = "none";
    btnText.innerHTML = "Read less"; 
    moreText.style.display = "inline";
  }
}