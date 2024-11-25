// src/components/sidebar/toggleButton.tsx
import React from 'react';
import { useSelector, useDispatch } from 'react-redux';
import { RootState } from '../../../store/store';
import { toggleSidebar } from '../../../store/slices/sidebarSlice';

const ToggleButton: React.FC = () => {
  const isSidebarOpen = useSelector((state: RootState) => state.sidebar.isOpen);
  const dispatch = useDispatch();

  const onToggle = () => {
    dispatch(toggleSidebar());
  };

  return (
      <img
        src="/assets/icon/collapseIcon.svg"
        alt="Toggle Sidebar"
        className={`h-12 rotate-180 bg-white rounded-md p-[10px] mt-10 cursor-pointer ${isSidebarOpen ? 'hidden':'md:block hidden'}`}
        onClick={onToggle}
      />
  );
};

export default ToggleButton;