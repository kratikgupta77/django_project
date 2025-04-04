from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Artifact, PaymentTransaction, Wallet
from .forms import ArtifactForm  
@login_required
def marketplace_home(request):
    """
    Landing page for the marketplace with options to sell, buy, or view payment history.
    """
    return render(request, "marketplace/landing.html")

@login_required
def sell_item(request):
    """
    Display a form to list a new artifact.
    """
    if request.method == "POST":
        form = ArtifactForm(request.POST, request.FILES)
        if form.is_valid():
            artifact = form.save(commit=False)
            artifact.seller = request.user.userprofile  
            artifact.save()
            return redirect('marketplace:artifact_detail', pk=artifact.pk)
    else:
        form = ArtifactForm()
    return render(request, "marketplace/sell_item.html", {'form': form})

@login_required
def artifact_list(request):
    """
    List all artifacts with optional search.
    """
    query = request.GET.get('q')
    if query:
        artifacts = Artifact.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        artifacts = Artifact.objects.all()
    return render(request, "marketplace/artifact_list.html", {'artifacts': artifacts, 'query': query})

@login_required
def artifact_detail(request, pk):
    """
    Display details for a single artifact.
    """
    artifact = get_object_or_404(Artifact, pk=pk)
    return render(request, "marketplace/artifact_detail.html", {'artifact': artifact})



def simulate_payment(request, pk):
    artifact = get_object_or_404(Artifact, pk=pk)
    buyer_profile = request.user.userprofile
    seller_profile = artifact.seller

    # Prevent the seller from buying their own item
    if buyer_profile == seller_profile:
        return render(request, "marketplace/simulate_payment.html", {
            'artifact': artifact, 
            'error': 'You cannot purchase your own listing.'
        })

    # Prevent buying an already sold item
    if artifact.sold:
        return render(request, "marketplace/simulate_payment.html", {
            'artifact': artifact, 
            'error': 'This item has already been sold.'
        })
    
    # Ensure both buyer and seller have wallets
    buyer_wallet, _ = Wallet.objects.get_or_create(user_profile=buyer_profile)
    seller_wallet, _ = Wallet.objects.get_or_create(user_profile=seller_profile)

    price = float(artifact.bidding_price)

    # Check if the buyer has enough balance
    if buyer_wallet.get_balance() < price:
        return render(request, "marketplace/simulate_payment.html", {
            'artifact': artifact, 
            'error': 'Insufficient funds.',
            'wallet_balance': buyer_wallet.get_balance()  # Pass wallet balance
        })

    # Deduct funds from buyer and credit seller
    buyer_wallet.update_balance(-price)
    seller_wallet.update_balance(price)

    # Mark artifact as sold
    artifact.sold = True
    artifact.save()
    
    # Record the transaction
    PaymentTransaction.objects.create(
        artifact=artifact,
        buyer=buyer_profile,
        seller=seller_profile,
        amount=price,
        status="completed"
    )
    
    return redirect('marketplace:artifact_list')


@login_required
def payment_history(request):
    """
    Display a list of payment transactions where the user is either the buyer or seller.
    """
    user_profile = request.user.userprofile
    transactions = PaymentTransaction.objects.filter(
        Q(buyer=user_profile) | Q(seller=user_profile)
    ).order_by('-created_at')
    return render(request, "marketplace/payment_history.html", {'transactions': transactions})
