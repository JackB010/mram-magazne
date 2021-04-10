$(".edit_span input").click((event) => {
  const item = $(event.target.parentElement).children()[1];
  $(item).slideToggle((duration = 100));
});
