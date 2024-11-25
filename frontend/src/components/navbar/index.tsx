import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { removeAllCookies } from '../../helpers/storage';
import { getCookies } from '../../helpers/storage';
import { useDispatch } from 'react-redux';
import { useSelector } from 'react-redux';
import { RootState } from '../../store/store';
import { AppDispatch } from '../../store/store';
import {jwtDecode} from 'jwt-decode';
import { toggleSidebar } from '../../store/slices/sidebarSlice';
import { Menu } from '../../icons';

interface JwtPayload {
  _id: string;
}
const Navbar: React.FC = () => {
  const navigate=useNavigate();
  const [dropdownOpen,setDropdownOpen]=useState(false);
  const dispatch = useDispatch<AppDispatch>();
  const isOpen = useSelector((state: RootState) => state.sidebar.isOpen);
  const onClose = () => {
    dispatch(toggleSidebar());
  };
  const toggleDropdown = () => {
    setDropdownOpen(!dropdownOpen);
  };
  let accessToken = getCookies('accessToken') as string;
  let refreshToken = getCookies('refreshToken');
  if(accessToken)
  {
    let decoded = jwtDecode(accessToken) as JwtPayload;
    var user_id = decoded._id;
  }
  const profile_logo="/assets/logo/user.svg";
  return (
    <nav className="w-full h-[79px] px-[24px] py-[16px] bg-gray-800 text-black flex justify-between items-center mx-auto opacity-100 fixed top-0 left-0 right-0 z-10 border-b border-white">
      <div className="flex items-center gap-2">
           <div onClick={onClose} className='md:hidden block'>
           <Menu width={24} height={18} />
            </div>
        <a href="/" className="flex items-center">
          <div className='text-white text-2xl font-bold'>
            FashionFiend
          </div>
        </a>
        

      </div>
      <div onClick={toggleDropdown} className='cursor-pointer border border-white rounded-full'>
        <img src={profile_logo} alt="Logo" className="h-8 rounded-[16px]" />
      </div>
      {dropdownOpen && (
                <div className="absolute flex flex-row top-10 right-2 mt-10 lg:w-[220px] w-[160px] bg-white rounded-md shadow-md cursor-pointer">
                  <button
                    className={`text-[14px] leading-[21px] w-full text-left py-[12px] pl-[22px] `}
                  >
                    Log Out
                  </button>
                  <img src="/assets/icon/Upload.svg" alt="Upload" className="lg:h-[20px] h-[15px] mr-4 mt-3" />
                </div>
              )}
    </nav>
  );
};

export default Navbar;
