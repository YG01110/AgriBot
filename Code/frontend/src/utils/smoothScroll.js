export const smoothScroll = (element) => {
    const target = element || document.documentElement;
    target.scrollTo({
      top: target.scrollHeight,
      behavior: 'smooth'
    });
  };