import Cookies from 'js-cookie';


export const getLocalStorage = (key: string) => {
    return localStorage.getItem(key)
}


export const setLocalStorage = (key: string, value: string) => {
    return localStorage.setItem(key, value)
}


export const getCookies = (key: string) => {
    return Cookies.get(key)
}

export const setCookies = (key: string, value: any) => {
    return Cookies.set(key, value)
}

export const removeCookies = (key: string) => {
    return Cookies.remove(key)
}


export const handleStoreCookie = (accessToken: string, refreshToken: string) => {  
  const newExpirationTime = new Date().getTime() + 9 * 60 * 1000;
  setCookies('tokenExpirationTime', newExpirationTime.toString());
  setCookies('accessToken', accessToken)
  setCookies('refreshToken', refreshToken)
}

export const removeAllCookies = () => {
    removeCookies('tokenExpirationTime')
    removeCookies('accessToken')
    removeCookies('refreshToken')
}