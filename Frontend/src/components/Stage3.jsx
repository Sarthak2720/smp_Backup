import { useGSAP } from '@gsap/react'
import gsap from 'gsap'
import { Database, Download, PrinterIcon, ShareIcon, ViewIcon } from 'lucide-react'
import { useEffect, useState } from 'react'
import { PiDetective } from 'react-icons/pi'
import { MoonLoader } from 'react-spinners'

const Stage3 = () => {
  const [loading, setLoading] = useState(false)

  // GSAP animation on load
  useGSAP(() => {
    gsap.from(".dialog", {
      scale: 0,
      y: -200,
      duration: 1,
      delay: 1,
      ease: "elastic.out(1,0.2)",
    })
  })

  // Simulate loading effect
  useEffect(() => {
    setLoading(true)
    setTimeout(() => {
      setLoading(false)
    }, 1000)
  }, [])

  // Function to handle PDF view
  const handleViewPDF = () => {
    window.open('/sample22.pdf', 'Parsed_data-pdf')  // Replace with the actual PDF file path
  }

  const handleViewPDF1 = () => {
    window.open('/ana.pdf', 'Suspicious_data-pdf')  // Replace with the actual PDF file path
  }

  return (
    <>
      <div className='dialog absolute font-semibold text-xl px-3 py-5 rounded-xl top-24 border-2 bg-white border-black'>
        Successfully Parsed! 🎉🎊
      </div>

      <div className='loginContainer bg-white border-2 border-black relative h-[60vh] flex flex-col gap-3 rounded-md w-[25vw] items-center'>
        {loading ? (
          <MoonLoader
            className='absolute top-10'
            color={"#000000"}
            loading={loading}
            size={50}
            aria-label="Loading Spinner"
            data-testid="loader"
          />
        ) : (
          <div className='flex flex-col gap-5 items-center p-3'>
            <h1 className='text-4xl font-medium underline underline-offset-8 cursor-default'>
              Data Summary
            </h1>

            <div className='px-3 py-2 rounded-lg border border-neutral-600 flex justify-between w-32 cursor-pointer'>
              <PrinterIcon /> Print
            </div>

            <div className='px-3 py-2 rounded-lg border border-neutral-600 flex justify-between w-32 cursor-pointer'>
              <Download /> Save
            </div>

            <div 
              className='px-3 py-2 rounded-lg border border-neutral-600 flex justify-between w-32 cursor-pointer'
              onClick={handleViewPDF}
            >
              <ViewIcon /> View
            </div>

            <div className='px-3 py-2 rounded-lg border border-neutral-600 flex justify-between w-32 cursor-pointer'>
              <ShareIcon /> Share
            </div>

            <div className='px-3 py-2 rounded-lg border border-neutral-600 flex justify-between w-32 cursor-pointer'>
              <Database /> Store
            </div>

            <div className='px-3 py-2 rounded-lg border border-neutral-600 flex justify-between w-32 cursor-pointer'
             onClick={handleViewPDF1}>
              <PiDetective size={25} /> Analyse
            </div>
          </div>
        )}
      </div>
    </>
  )
}

export default Stage3
