# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

from botbuilder.dialogs import (
    ComponentDialog,
    WaterfallDialog,
    WaterfallStepContext,
    DialogTurnResult,
)
from botbuilder.dialogs.prompts import (
    TextPrompt,
    NumberPrompt,
    ChoicePrompt,
    ConfirmPrompt,
    AttachmentPrompt,
    PromptOptions,
    PromptValidatorContext,
)
from botbuilder.dialogs.choices import Choice
from botbuilder.core import MessageFactory, UserState

from data_models import UserProfile

# greet

class UserProfileDialog(ComponentDialog):
    def __init__(self, user_state: UserState):
        super(UserProfileDialog, self).__init__(UserProfileDialog.__name__)

        self.user_profile_accessor = user_state.create_property("UserProfile")

        self.add_dialog(
            WaterfallDialog(
                WaterfallDialog.__name__,
                [
                    self.support_mode_step,
                    self.kind_step,
                    self.genre_step,
                    self.duration_step,
                    self.spread_step,
                    self.contact_step,
                    self.time_step,
                    self.confirm_step,
                    self.summary_step,
                ],
            )
        )
        self.add_dialog(TextPrompt(TextPrompt.__name__))
        self.add_dialog(ChoicePrompt(ChoicePrompt.__name__))
        self.add_dialog(ConfirmPrompt(ConfirmPrompt.__name__))

        self.initial_dialog_id = WaterfallDialog.__name__

    async def support_mode_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:
        # WaterfallStep always finishes with the end of the Waterfall or with another dialog;
        # here it is a Prompt Dialog. Running a prompt here means the next WaterfallStep will
        # be run when the users response is received.
        await step_context.context.send_activity(
            MessageFactory.text("Hello, I'm sorry to hear that you are having tech issues. I am the Service Help Bot, and I hope I can help you work things out!") #welcome message
        )
        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Would you like to Create a Service Request or Talk to a Representative?"),
                choices=[Choice("Service Request"), Choice("Representative")],
            ),
        )

    # Service Request asks more questions than Representative, but both paths unite at the end when asking for contact information
    # inserts service type into values["kind"], all following functions check which option was chosen and determines to ask a question (Service Request) or skip (Representative)

    async def kind_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
    
        step_context.values["kind"] = step_context.result.value

        if step_context.values["kind"] == "Representative":            
            return await step_context.next(0)

        elif step_context.values["kind"] == "Service Request":
            
            return await step_context.prompt(
                ChoicePrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("Please choose the option that best describes your issue"),
                    choices=[Choice("PC Desktop"), Choice("iMac"), Choice("PC Laptop"), 
                        Choice("Mac Laptop"), Choice("Linux"), Choice("Phone"), 
                        Choice("Tablet"), Choice("Internet"), Choice("TV")],
                ),
            )

        else: # error checking
            await step_context.context.send_activity(
                MessageFactory.text("Error in kind_confirm_step")
            )

        # WaterfallStep always finishes with the end of the Waterfall or
        # with another dialog; here it is a Prompt Dialog.

    async def genre_step(self,step_context: WaterfallStepContext) -> DialogTurnResult:
        
        if step_context.values["kind"] == "Representative":
            return await step_context.next(0)

        elif step_context.values["kind"] == "Service Request":
        # doesn't need to check if genre is among choices, user can enter their own genre
            step_context.values["genre"] = step_context.result.value

            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("How long has this issue persisted?"),
                ),
            )

        else:
            await step_context.context.send_activity(
                MessageFactory.text("Error in genre_step")
            )
        
    async def duration_step(self,step_context: WaterfallStepContext) -> DialogTurnResult:
        
        if step_context.values["kind"] == "Representative": #checking if ["kind"] is Representative; skips if true
            return await step_context.next(0)

        elif step_context.values["kind"] == "Service Request":
            
            step_context.values["duration"] = step_context.result
            
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                    prompt=MessageFactory.text("How many others are experiencing this issue right now?"),
                )
            )

        else:
            await step_context.context.send_activity(
                MessageFactory.text("Error in duration_step")
            )

    async def spread_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        step_context.values["spread"] = step_context.result

        return await step_context.prompt(
            ChoicePrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("How would you like to be contacted for support today?"),
                choices=[Choice("Phone Number"), Choice("Email")],
            ),
        )

    async def contact_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        step_context.values["contact"] = step_context.result.value

        if step_context.values["contact"] == "Phone Number":
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                prompt=MessageFactory.text("Please enter your phone number"),
                ),
            )

        else:
            return await step_context.prompt(
                TextPrompt.__name__,
                PromptOptions(
                prompt=MessageFactory.text("Please enter your email"),
                ),  
            )

    async def time_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:
                
        step_context.values["contact"] = step_context.result

        return await step_context.prompt(
            TextPrompt.__name__,
            PromptOptions(
                prompt=MessageFactory.text("Please enter the best time to contact you"),
            ),
        )


    async def confirm_step(self, step_context: WaterfallStepContext) -> DialogTurnResult:

        step_context.values["time"] = step_context.result

        # WaterfallStep always finishes with the end of the Waterfall or
        # with another dialog; here it is aConfirmPrompt Dialog.
        

        return await step_context.prompt(
            ConfirmPrompt.__name__,
            PromptOptions(prompt=MessageFactory.text("Are you sure?")),
        )

    async def summary_step(
        self, step_context: WaterfallStepContext
    ) -> DialogTurnResult:

        #User picks Yes
        if step_context.result:
            # Get the current profile object from user state.  Changes to it
            # will saved during Bot.on_turn.
            user_profile = await self.user_profile_accessor.get(
                step_context.context, UserProfile
            )

            user_profile.kind = step_context.values["kind"]
            user_profile.contact = step_context.values["contact"]
            user_profile.time = step_context.values["time"]
            user_profile.ticket = 27081114610276727

            msg_1 = f"Support type: {user_profile.kind}."
            msg_2 = ""
            await step_context.context.send_activity(
                MessageFactory.text(msg_1)
            )

            #customized message based on support path

            if user_profile.kind == "Service Request":
                
                user_profile.genre = step_context.values["genre"]
                user_profile.duration = step_context.values["duration"]
                user_profile.spread = step_context.values["spread"]

                msg_2 += f" Nature of issue: {user_profile.genre}. Duration of issue: {user_profile.duration}. Others affected:{user_profile.spread}"
       
            msg_2 += f" Contact information: {user_profile.contact}."
        
            await step_context.context.send_activity(
                MessageFactory.text(msg_2)
            )
            await step_context.context.send_activity(
                MessageFactory.text(f"A technical support specialist has been notified and will contact you. Chosen time: {user_profile.time}. A ticket has been created for this issue.")
            )
            await step_context.context.send_activity(
                MessageFactory.text(f"Support ticket number: {user_profile.ticket}")
            )

        #User picked no
        else:
            await step_context.context.send_activity(
                MessageFactory.text("Ok. Your ticket will not be created.") 
            )

        await step_context.context.send_activity(
            MessageFactory.text("Type anything to run the bot again")
        )

        # WaterfallStep always finishes with the end of the Waterfall or with another
        # dialog, here it is the end.
        return await step_context.end_dialog()
