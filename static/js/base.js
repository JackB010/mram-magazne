const burger = document.querySelector('.burger');
const navLinks = document.querySelector('.links');
const links = document.querySelectorAll('.links li');
const toTop = document.querySelector('.to-top');



$(".edit_span button").click((event) => {
  const item = $(event.target.parentElement).children()[1];
  $(item).slideToggle((duration = 100));
});

$(".edit_span i").click((event) => {
  const item = $(event.target.parentElement).children()[1];
  $(item).slideToggle((duration = 100));
});



burger.addEventListener("click", () => {
  navLinks.classList.toggle('active');

  //the Links Fade
  links.forEach(link => {
    link.classList.toggle('fade');
  });
  //the X transition
  burger.classList.toggle('toggle');
});