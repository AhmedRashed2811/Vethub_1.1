const ProfileUpload = (event) => {
    const files = event.target.files;
    const filesLength = files.length;
    if (filesLength > 0) {
      const imageSrc = URL.createObjectURL(files[0]);
      const imagePreviewElement = document.querySelector(".Authentication-page .container .Section-2 form .tb-container .ProfilePhoto .image");
    //   imagePreviewElement.src = imageSrc;
    console.log(imageSrc);
      imagePreviewElement.style.backgroundImage = `url(${imageSrc})`;
    }
};
const CertificationUpload = (event) => {
    const files = event.target.files;
    const filesLength = files.length;
    if (filesLength > 0) {
      const imageSrc = URL.createObjectURL(files[0]);
      const imagePreviewElement = document.querySelector(".Authentication-page .container .Section-2 form .tb-container .Certification .image");
    //   imagePreviewElement.src = imageSrc;
    console.log(imageSrc);
      imagePreviewElement.style.backgroundImage = `url(${imageSrc})`;
    }
};
const ProfileUpdate = (event) => {
  const files = event.target.files;
  const filesLength = files.length;
  if (filesLength > 0) {
    const imageSrc = URL.createObjectURL(files[0]);
    const imagePreviewElement = document.querySelector(".profile .Body img");
    imagePreviewElement.src = imageSrc;
    console.log(imageSrc);
    // imagePreviewElement.style.backgroundImage = `url(${imageSrc})`;
  }
};
function newsPhoto(event) {
  const files = event.target.files;
  const filesLength = files.length;
  if (filesLength > 0) {
    const imageSrc = URL.createObjectURL(files[0]);
    const imagePreviewElement = document.querySelector("body .manageNews form .tb-container label .image");
    imagePreviewElement.style.backgroundImage = `url(${imageSrc})`;
  }
}

const governorateSelect = document.getElementById("governorate-select");

const regionSelect = document.getElementById("region-select");

function updateRegionOptions() {
  const selectedGovernorate = governorateSelect?.value;
  console.log(regionSelect);
  regionSelect.innerHTML = "<option value='' disabled selected>Chose Area</option>";
  if (selectedGovernorate && data[selectedGovernorate]) {
    data[selectedGovernorate].forEach(region => {
      const option = document.createElement("option");
      option.textContent = region;
      option.value = region;
      regionSelect.appendChild(option);
    });
  }
}

governorateSelect?.addEventListener("change", updateRegionOptions);

for (const governorate in data) {
  if (data.hasOwnProperty(governorate)) {
    const option = document.createElement("option");
    option.textContent = governorate;
    option.value = governorate;
    governorateSelect?.appendChild(option);
  }
}



/* Notification */
const notification = document.querySelector(".navbar .container .nav-item .Notification");
const bill = document.querySelector(".navbar .container .nav-item .BillFather");
const bgBill = document.querySelectorAll(".navbar .container .nav-item .BillFather .BillHover");

bill?.addEventListener("click", () => {
  notification.classList.toggle("notificationshow");
  bgBill.forEach((element) => {
    element.classList.toggle("BillColor");
  });
});

// Form Section
var answerQuestionOneElements = document.querySelectorAll('.formBody .form form .question1 .answers .answer');

answerQuestionOneElements.forEach(function(answerElement) {
    answerElement.addEventListener('click', function() {
        answerQuestionOneElements.forEach(function(element) {
            element.querySelector('.formBody .form form .question1 .answers .answer .circle').classList.remove('choose');
          });
        answerElement.querySelector('.formBody .form form .question1 .answers .answer .circle').classList.toggle('choose');
    });
});

var answerQuestionTwoElements = document.querySelectorAll('.formBody .form form .question2 .answers .answer');

answerQuestionTwoElements.forEach(function(answerElement) {
    answerElement.addEventListener('click', function() {
        answerQuestionTwoElements.forEach(function(element) {
            element.querySelector('.formBody .form form .question2 .answers .answer .circle').classList.remove('choose');
          });
        answerElement.querySelector('.formBody .form form .question2 .answers .answer .circle').classList.toggle('choose');
    });
});

// Rating Stars
const stars = document.querySelectorAll('.formBody .form form .question4 .answers .stars i');

stars.forEach((star, index) => {
  star.addEventListener('click', () => {
    toggleStars(index);
  });
});

function toggleStars(index) {
  for (let i = 0; i <= index; i++) {
    stars[i].classList.remove('fa-regular');
    stars[i].classList.add('fa-solid');
  }

  for (let i = index + 1; i < stars.length; i++) {
    stars[i].classList.remove('fa-solid');
    stars[i].classList.add('fa-regular');
  }
}

// Book Time
var timeElements = document.querySelectorAll('.bookingInformation .reservationDate .days .day .time');

// Add click event listener to each 'time' element
timeElements.forEach(function(element) {
  var allFooters = document.querySelectorAll('.bookingInformation .reservationDate .days .day .footer');
  allFooters.forEach(function(footer) {
      footer.disabled = true
  });

  element.addEventListener('click', function() {
      if (!element.classList.contains('booked')) {
        timeElements.forEach(function(el) {
          el.classList.remove('choose');
        });
        element.classList.add('choose');
        
        var allFooters = document.querySelectorAll('.bookingInformation .reservationDate .days .day .footer');
        allFooters.forEach(function(footer) {
          footer.classList.remove('green');
        });
        
        var dayElement = element.closest('.day');
        if (dayElement) {
          var footerElement = dayElement.querySelector('.footer');
          
          if (footerElement) {
            footerElement.classList.add('green');
            allFooters.forEach(function(footer) {
              if (footer == footerElement){footer.disabled = false}
              else{
                  footer.disabled = true
              }
            });
          }
        }
      }
        
  });
});

// User profile Function password
function togglePassword() {
  const passwordInput = document.getElementById("password");
  const togglePasswordIcon = document.querySelector(".toggle-password");
  if (passwordInput.type === "password") {
      passwordInput.type = "text";
      togglePasswordIcon.style.background = "url('imgs/close-eye.png')";
  } else {
      passwordInput.type = "password";
      togglePasswordIcon.style.background = "url('imgs/open-eye.png')";
  }
}

// Doctor Details Slider

var swiper = new Swiper('.swiper', {
  slidesPerView: 3,
  navigation: {
    nextEl: '.swiper-button-next',
    prevEl: '.swiper-button-prev',
  },
  breakpoints: {
    0: {
      slidesPerView: 1,
    },
    338: {
      slidesPerView: 3,
    },
    481:{
      slidesPerView: 2,
    },
    520: {
      slidesPerView: 3,
    },
    630: {
      slidesPerView: 4,
    },
    992: {
      slidesPerView: 2,
    },
    1200: {
      slidesPerView: 3,
    },
    // 1400:{
    //   slidesPerView: 4,
    // },
  },
});


// See More Time
let moreButtons = document.querySelectorAll('#morex');

moreButtons.forEach(function(button) {
    button?.addEventListener('click', function() {
      let container = button.parentElement;
      let times = container.querySelectorAll('.time');

      times.forEach(function(time) {
          time.style.display = 'inline-block';
      });
      
      button.style.display = 'none';
    });
});

// See More Comments
let seeMore = document.querySelector('#see-more');
let currentItem = 3;

seeMore?.addEventListener('click', function() {
  let boxes = [...document.querySelectorAll('.doctorDetails .AllComments .comments .comment')];
  for (let i = currentItem; i < boxes.length ; i++) {
    boxes[i].style.display = 'flex';
  }
  seeMore.style.display = 'none';
})



