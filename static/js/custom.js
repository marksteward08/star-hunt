Element.prototype.replaceClass = function (class1, class2) {
    this.classList.remove(class1);
    this.classList.add(class2);
}