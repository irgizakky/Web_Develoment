document.addEventListener('DOMContentLoaded', () => {
    const learnMoreBtn = document.querySelector('a.btn.btn-outline[href="#about-section"]');
    if (learnMoreBtn) {
        learnMoreBtn.addEventListener('click', (e) => {
            e.preventDefault();
            const target = document.getElementById('about-section');
            if (target) {
                target.scrollIntoView({ behavior: 'smooth' });
            }
        });
    }

    const featureBoxes = document.querySelectorAll('.feature-box');
    if ('IntersectionObserver' in window && featureBoxes.length) {
        featureBoxes.forEach(box => box.classList.add('feature-hidden'));

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('feature-show');
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.2 });

        featureBoxes.forEach(box => observer.observe(box));
    }
});
