import { toast } from 'react-toastify';

const CommonProps: any = ({ options = {} }: any = {}) => {
    return {
        position: "top-center",
        autoClose: 8000,
        hideProgressBar: false,
        closeOnClick: true,
        pauseOnHover: true,
        draggable: true,
        progress: undefined,
        theme: "light",
        closeButton: true,
        ...options
    }
}

const toastSuccess = ({ message, options }: any) => {
    toast.dismiss()
    return toast.success(message,
        { ...CommonProps({ options }) }
    )
}

const toastError = ({ message, errors }: any) => {
    toast.dismiss()
    return toast.error(
        message,
        { ...CommonProps() }
    )
}

const toastInfo = ({ message }: any) => {
    toast.dismiss()
    return toast.info(
        message,
        { ...CommonProps() }
    )
}

const toastWarning = ({ message }: any) => {
    toast.dismiss()
    return toast.warn(
        message,
        { ...CommonProps() }
    )

}


export { toastSuccess, toastError, toastInfo, toastWarning }