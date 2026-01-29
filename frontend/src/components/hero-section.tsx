import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from '@/components/ui/button'
import { HeroHeader } from './header'
import { InfiniteSlider } from '@/components/ui/infinite-slider'
import { ProgressiveBlur } from '@/components/ui/progressive-blur'
import { useAuthStore } from '@/store/useAuthStore'

export default function HeroSection() {
    const { authUser } = useAuthStore()

    return (
        <>
            <HeroHeader />
            <main className="overflow-x-hidden">
                <section>
                    <div className="pb-24 pt-12 md:pb-32 lg:pb-56 lg:pt-44">
                        <div className="relative mx-auto flex max-w-6xl flex-col px-6 lg:block">
                            <div className="mx-auto max-w-lg text-center lg:ml-0 lg:w-1/2 lg:text-left">
                                <h1 className="mt-8 max-w-2xl text-balance text-5xl font-medium md:text-6xl lg:mt-16 xl:text-7xl">Accelerate Drug Discovery with AI</h1>
                                <p className="mt-8 max-w-2xl text-pretty text-lg">Harnessing advanced artificial intelligence to identify therapeutic targets and predict molecular interactions with unprecedented speed and accuracy.</p>

                                <div className="mt-12 flex flex-col items-center justify-center gap-2 sm:flex-row lg:justify-start">
                                    {authUser ? (
                                        <Button
                                            asChild
                                            size="lg"
                                            className="px-5 text-base">
                                            <Link to="/dashboard">
                                                <span className="text-nowrap">Go to Dashboard</span>
                                            </Link>
                                        </Button>
                                    ) : (
                                        <>
                                            <Button
                                                asChild
                                                size="lg"
                                                className="px-5 text-base">
                                                <Link to="/signup">
                                                    <span className="text-nowrap">Start Discovery</span>
                                                </Link>
                                            </Button>
                                            <Button
                                                asChild
                                                size="lg"
                                                variant="ghost"
                                                className="px-5 text-base">
                                                <Link to="/login">
                                                    <span className="text-nowrap">Login to access</span>
                                                </Link>
                                            </Button>
                                        </>
                                    )}
                                </div>
                            </div>
                            <img
                                className="-z-10 order-first ml-auto h-64 w-full object-cover sm:h-96 lg:absolute lg:inset-y-0 lg:right-[-10%] lg:h-full lg:w-[60%] lg:order-last [mask-image:radial-gradient(circle_at_center,black_40%,transparent_100%)] contrast-125 saturate-110 dark:mix-blend-screen"
                                src="/drug_discovery_hero.png"
                                alt="Drug Discovery AI"
                            />
                        </div>
                    </div>
                </section>

            </main>
        </>
    )
}
