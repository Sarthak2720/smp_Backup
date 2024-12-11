import { FaFacebook, FaGoogle, FaInstagram, FaTelegram, FaWhatsapp } from 'react-icons/fa'
import { FaTwitter } from 'react-icons/fa6'
import { Link } from 'react-router-dom'

const LoginContainer = () => {
  return (
    <div className='loginContainer h-[50vh] flex flex-col gap-3 rounded-xl w-[30vw] border-2 border-black bg-white'>
      <div className='flex justify-evenly p-6'>
        <p className='rounded-full border border-black px-2 py-1 '>1</p>
        <p className='rounded-full border border-black px-2 py-1 '>2</p>
        <p className='rounded-full border border-black px-2 py-1 '>3</p>
      </div>
      <h1 className='text-3xl text-center font-medium'>Select The Social Media</h1>
      <div className="social-btns">
        {/* Passing platform name as URL parameter to AccusedData */}
        <Link to="/accusedData/facebook">
          <a className="btn facebook border-[0.2px] border-black">
            <FaFacebook className='fa' />
          </a>
        </Link>
        <Link to="/accusedData/twitter">
          <a className="btn twitter border-[0.2px] border-black">
            <FaTwitter className='fa' />
          </a>
        </Link>
        <Link to="/accusedData/google">
          <a className="btn google border-[0.2px] border-black">
            <FaGoogle className='fa' />
          </a>
        </Link>
        <Link to="/accusedData/telegram">
          <a className="btn dribbble border-[0.2px] border-black">
            <FaTelegram className='fa' />
          </a>
        </Link>
        <Link to="/accusedData/whatsapp">
          <a className="btn skype border-[0.2px] border-black">
            <FaWhatsapp className='fa' />
          </a>
        </Link>
        <Link to="/accusedData/instagram">
          <a className="btn instagram border-[0.2px] border-black text-white">
            <FaInstagram className='fa rounded-xl' />
          </a>
        </Link>
      </div>
    </div>
  )
}

export default LoginContainer
