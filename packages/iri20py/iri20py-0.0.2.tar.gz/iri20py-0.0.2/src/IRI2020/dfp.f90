      subroutine dfp(direct,filename, path)
         implicit none
         character(len=*), intent(in)  :: filename, direct
         character(len=256), intent(inout) :: path

         character(len=:), allocatable :: trimmed_dir
         integer :: dir_len

         ! --- Trim leading/trailing blanks from directory ---
         ! write(6,*) 'Input dir: ', direct 
         trimmed_dir = trim(adjustl(direct))
         ! write(6,*) 'Adjusted input: ', trimmed_dir
         ! write(6,*) 'Input file: ', filename
         dir_len = len_trim(trimmed_dir)
         select case (dir_len)
          case (0)
            ! If directory is blank, just use filename (truncated/padded to 256)
            path = filename
          case default
            ! Check if directory ends with '/'
            if (trimmed_dir(dir_len:dir_len) /= '/') then
               path = trimmed_dir // '/' // filename
            else
               path = trimmed_dir // filename
            end if
         end select

         ! Truncate or pad to 256 characters if needed
         if (len_trim(path) < 256) then
            path = adjustl(path) // repeat(' ', 256 - len_trim(path))
         else if (len_trim(path) > 256) then
            path = path(1:256)
         end if
         ! write(6,*) 'Output path: ', path
      end subroutine dfp
