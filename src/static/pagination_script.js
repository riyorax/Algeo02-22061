 
 const galleryItems=document.querySelector(".gallery-items").children;
 const prev=document.querySelector(".prev");
 const next=document.querySelector(".next");
 const page=document.querySelector(".page-num");
 const maxItem=12;
 let index=1;
  
  const pagination=Math.ceil(galleryItems.length/maxItem);

  prev.addEventListener("click",function(){
    index--;
    check();
    showItems();
  })
  next.addEventListener("click",function(){
  	index++;
  	check();
    showItems();  
  })

  function check(){
  	 if(index==pagination){
  	 	next.classList.add("disabled");
  	 }
  	 else{
  	   next.classList.remove("disabled");	
  	 }

  	 if(index==1){
  	 	prev.classList.add("disabled");
  	 }
  	 else{
  	   prev.classList.remove("disabled");	
  	 }
  }

  function showItems() {
  	 for(let i=0;i<galleryItems.length; i++){
  	 	galleryItems[i].classList.remove("show");
  	 	galleryItems[i].classList.add("hide");


  	    if(i>=(index*maxItem)-maxItem && i<index*maxItem){
          galleryItems[i].classList.remove("hide");
          galleryItems[i].classList.add("show");
  	    }
  	    page.innerHTML=index;
  	 }

  	 	
  }

  window.onload=function(){
  	showItems();
  	check();
  }




  var currentPage = 1;
  var totalPages = 1;

  function renderImages(images) {
	  var imageContainer = document.getElementById('image-container');
	  imageContainer.innerHTML = '';

	  images.forEach(function(imageUrl) {
		  var img = document.createElement('img');
		  img.src = "{{ url_for('static', filename='images/') }}" + imageUrl;
		  imageContainer.appendChild(img);
	  });

	  document.getElementById('page-num').innerText = currentPage;
  }

  function changePage(offset) {
	  currentPage += offset;
	  if (currentPage < 1) {
		  currentPage = 1;
	  } else if (currentPage > totalPages) {
		  currentPage = totalPages;
	  }

	  updatePageDropdown();
	  fetchImages();
  }

  function changePageDropdown(select) {
	  currentPage = parseInt(select.value);
	  fetchImages();
  }

  function updatePageDropdown() {
	  var select = document.getElementById('page-select');
	  select.innerHTML = '';

	  for (var i = 1; i <= totalPages; i++) {
		  var option = document.createElement('option');
		  option.value = i;
		  option.text = i;
		  select.appendChild(option);
	  }

	  select.value = currentPage;
  }

  function fetchImages() {
	  fetch('/get_images', {
		  method: 'POST',
		  headers: {
			  'Content-Type': 'application/json'
		  },
		  body: JSON.stringify({ 'page': currentPage })
	  })
	  .then(response => response.json())
	  .then(data => {
		  totalPages = data.total_pages;
		  renderImages(data.images);
		  updatePageDropdown();
	  })
	  .catch(error => console.error('Error:', error));
  }

  function downloadData() {
	  fetch('/get_images', {
		  method: 'POST',
		  headers: {
			  'Content-Type': 'application/json'
		  },
		  body: JSON.stringify({ 'page': currentPage })
	  })
	  .then(response => response.json())
	  .then(data => {
		  var jsonDataString = JSON.stringify(data, null, 2);
		  var blob = new Blob([jsonDataString], { type: 'application/json' });
		  var url = URL.createObjectURL(blob);

		  var a = document.createElement('a');
		  a.href = url;
		  a.download = 'algeo_data.json';
		  document.body.appendChild(a);
		  a.click();
		  document.body.removeChild(a);
	  })
	  .catch(error => console.error('Error:', error));
  }

  fetchImages();






